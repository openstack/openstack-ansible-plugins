# Copyright 2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2016, Kevin Carter <kevin.carter@rackspace.com>

import copy
import imp
import os

# NOTICE(cloudnull): The connection plugin imported using the full path to the
#                    file because the linear strategy plugin is not importable.
import ansible.plugins.strategy as strategy
LINEAR = imp.load_source(
    'ssh',
    os.path.join(os.path.dirname(strategy.__file__), 'linear.py')
)

# NOTICE(jmccrory): The play_context is imported so that additional container
#                   specific variables can be made available to connection
#                   plugins.
import ansible.playbook.play_context
ansible.playbook.play_context.MAGIC_VARIABLE_MAPPING.update({'physical_host':
                                                           ('physical_host',)})
ansible.playbook.play_context.MAGIC_VARIABLE_MAPPING.update({'container_name':
                                                           ('inventory_hostname',)})
ansible.playbook.play_context.MAGIC_VARIABLE_MAPPING.update({'chroot_path':
                                                           ('chroot_path',)})
ansible.playbook.play_context.MAGIC_VARIABLE_MAPPING.update({'container_tech':
                                                           ('container_tech',)})

class StrategyModule(LINEAR.StrategyModule):
    """Notes about this strategy.

    When this strategy encounters a task with a "when" or "register" stanza it
    will collect results immediately essentially forming a block. If the task
    does not have a "when" or "register" stanza the results will be collected
    after all tasks have been queued.

    To improve execution speed if a task has a "when" conditional attached to
    it the conditional will be rendered before queuing the task and should the
    conditional evaluate to True the task will be queued. To ensure the correct
    execution of playbooks this optimisation will only be used if there are no
    lookups used with the task which is to guarantee proper task execution.

    To optimize transport reliability if a task is using a "delegate_to" stanza
    the connection method will change to paramiko if the connection option has
    been set at "smart", the Ansible 2.x default. Regardless of the connection
    method if a "delegate_to" is used the task will have pipelining disabled
    for the duration of that specific task.

    Container context will be added to the ``playbook_context`` which is used
    to further optimise connectivity by only ever SSH'ing into a given host
    machine instead of attempting an SSH connection into a container.
    """

    @staticmethod
    def _check_when(host, task, templar, task_vars):
        """Evaluate if conditionals are to be run.

        This will error on the side of caution:
            * If a conditional is detected to be valid the method will return
              True.
            * If there's ever an issue with the templated conditional the
              method will also return True.
            * If the task has a detected "with" the method will return True.

        :param host: object
        :param task: object
        :param templar: object
        :param task_vars: dict
        """
        try:
            if not task.when or (task.when and task.register):
                return True

            _ds = getattr(task, '_ds', dict())
            if any([i for i in _ds.keys() if i.startswith('with')]):
                return True

            conditional = task.evaluate_conditional(templar, task_vars)
            if not conditional:
                LINEAR.display.verbose(
                    u'Task "%s" has been omitted from the job because the'
                    u' conditional "%s" was evaluated as "%s"'
                    % (task.name, task.when, conditional),
                    host=host,
                    caplevel=0
                )
                return False
        except Exception:
            return True
        else:
            return True

    def _queue_task(self, host, task, task_vars, play_context):
        """Queue a task to be sent to the worker.

        Set a host variable, 'physical_host_addrs', containing a dictionary of
        each physical host and its 'ansible_host' variable.

        Modify the playbook_context to disable pipelining and use the paramiko
        transport method when a task is being delegated.
        """
        templar = LINEAR.Templar(loader=self._loader, variables=task_vars)
        if not self._check_when(host, task, templar, task_vars):
            return

        _play_context = copy.deepcopy(play_context)

        pha = task_vars['physical_host_addrs'] = dict()
        physical_host_items = [task_vars.get('physical_host')]
        if task.delegate_to:
            # For delegated tasks, we also need the information from the delegated hosts
            for delegated_host in task_vars.get('ansible_delegated_vars', dict()).keys():
                LINEAR.display.verbose(
                    u'Task is delegated to %s.' % delegated_host,
                    host=host,
                    caplevel=0
                )
                delegated_host_info = self._inventory.get_host(u'%s' % delegated_host)
                # This checks if we are delegating to a host which does not exist
                # in the inventory (possibly using its IP address)
                if delegated_host_info is None:
                    continue
                physical_host_vars = delegated_host_info.get_vars()
                physical_host_templar = LINEAR.Templar(loader=self._loader,
                                                       variables=physical_host_vars)
                delegated_physical_host = physical_host_templar.template(
                    physical_host_vars.get('physical_host'))
                if delegated_physical_host:
                    physical_host_items.append(delegated_physical_host)
                    LINEAR.display.verbose(
                        u'Task is delegated to %s. Adding its physical host %s'
                        % (delegated_host, delegated_physical_host),
                        host=host,
                        caplevel=0
                    )
        for physical_host_item in physical_host_items:
            ph = self._inventory.get_host(physical_host_item)
            if ph:
                LINEAR.display.verbose(
                    u'The "physical_host" variable of "%s" has been found to'
                    u' have a corresponding host entry in inventory.'
                    % physical_host_item,
                    host=host,
                    caplevel=0
                )
                physical_host_vars = self._variable_manager.get_vars(host=ph)
                for item in ['ansible_host', 'container_address', 'address']:
                    addr = ph.vars.get(item)
                    if addr:
                        LINEAR.display.verbose(
                            u'The "physical_host" variable of "%s" terminates'
                            u' at "%s" using the host variable "%s".' % (
                                physical_host_item,
                                addr,
                                item
                            ),
                            host=host,
                            caplevel=0
                        )
                        pha[ph.name] = addr
                        host.set_variable('physical_host_addrs', pha)
                        break


        if task.delegate_to:
            # If a task uses delegation change the play_context
            #  to use paramiko with pipelining disabled for this
            #  one task on its collection of hosts.
            if _play_context.pipelining:
                _play_context.pipelining = False
                LINEAR.display.verbose(
                    u'Because this is a task using "delegate_to"'
                    u' pipelining has been disabled. but will be'
                    u' restored upon completion of this task.',
                    host=host,
                    caplevel=0
                )

            if _play_context.connection == 'smart':
                _play_context.connection = 'paramiko'
                LINEAR.display.verbose(
                    u'Delegated task transport changing from'
                    u' "%s" to "%s". The context will be restored'
                    u' once the task has completed.' % (
                        _play_context.connection,
                        _play_context.connection
                    ),
                    host=host,
                    caplevel=0
                )

        return super(StrategyModule, self)._queue_task(
            host,
            task,
            task_vars,
            _play_context
        )
