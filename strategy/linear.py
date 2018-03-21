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

# NOTICE(jmccrory): MAGIC_VARIABLE_MAPPING is imported so that additional
#                   container specific variables can be made available to
#                   the connection plugin.
#                   In Ansible 2.5 the magic variable mapping has been moved,
#                   but updating it directly is no longer necessary. The
#                   variables can be made available through being defined in
#                   the connection plugin's docstring and this can eventually
#                   be removed.
try:
    from ansible.playbook.play_context import MAGIC_VARIABLE_MAPPING
    MAGIC_VARIABLE_MAPPING.update({
        'physical_host': ('physical_host',),
        'container_name': ('inventory_hostname',),
        'chroot_path': ('chroot_path',),
        'container_tech': ('container_tech',),
        'container_user': ('container_user',),
    })
except ImportError:
    pass

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

        try:
            groups = self._inventory.get_groups_dict()
        except AttributeError:
            groups = self._inventory.get_group_dict()
        physical_hosts = groups.get('hosts', groups.get('all', {}))
        physical_host_addrs = {}
        for physical_host in physical_hosts:
            physical_host_vars = self._inventory.get_host(physical_host).vars
            physical_host_addr = physical_host_vars.get('ansible_host',
                                                        physical_host)
            physical_host_addrs[physical_host] = physical_host_addr
        host.set_variable('physical_host_addrs', physical_host_addrs)

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
