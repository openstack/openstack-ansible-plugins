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

DOCUMENTATION = '''
    connection: ssh
    short_description: connect via ssh client binary
    description:
        - This connection plugin allows ansible to communicate to the target machines via normal ssh command line.
    author: ansible (@core)
    version_added: historical

    # import all existing options from the ansible.builtin.ssh connection plugin
    extends_documentation_fragment: openstack.osa.builtin_ssh_fragment

    # define additional options that extend the builtin connection plugin
    options:
      container_name:
          description: Hostname of a container
          vars:
               - name: container_name
      container_user:
          description: Username used when running command inside a container
          vars:
               - name: container_user
      physical_host_addrs:
          description: Dictionary mapping of physical hostnames and their ip addresses
          vars:
               - name: physical_host_addrs
      physical_host:
          description: Hostname of host running a given container
          vars:
               - name: physical_host
'''

import importlib
import os

from ansible.module_utils.six.moves import shlex_quote

SSH = importlib.import_module('ansible.plugins.connection.ssh')

class Connection(SSH.Connection):
    """Transport options for containers.

    This transport option makes the assumption that the playbook context has
    vars within it that contain "physical_host" which is the machine running a
    given container and "container_name" which is the actual name of the
    container. These options can be added into the playbook via vars set as
    attributes or though the modification of the a given execution strategy to
    set the attributes accordingly.

    This plugin operates exactly the same way as the standard SSH plugin but
    will pad pathing or add command syntax for containers when a container
    is detected at runtime.
    """

    transport = 'ssh'

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.container_name = None
        self.physical_host = None

        # Store the container pid for multi-use
        self.container_pid = None
        self.is_container = None

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(Connection, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.container_name = self.get_option('container_name')
        self.physical_host = self.get_option('physical_host')

        # Check to see if container_user is setup first, if so use that value.
        # If it isn't, then default to 'root'
        # The connection's shell plugin also needs to be initialized here and
        # updated to use a system writable temp directory to avoid requiring
        # that container_user have sudo privileges.
        self.container_user = self.get_option('container_user') or 'root'
        if self.container_user != 'root':
            self._shell.set_options(var_options={})
            self._shell.set_option('remote_tmp', self._shell.get_option('system_tmpdirs')[0])

        self.is_container = self._container_check()

        if self.is_container:
            physical_host_addrs = self.get_option('physical_host_addrs') or {}
            if self.host in physical_host_addrs.values():
                self.container_name = None
            else:
                self._set_physical_host_addr(physical_host_addrs)

    def _set_physical_host_addr(self, physical_host_addrs):
        physical_host_addr = physical_host_addrs.get(self.physical_host,
                                                     self.physical_host)
        self.host = self._options['host'] = self._play_context.remote_addr = physical_host_addr

    def exec_command(self, cmd, in_data=None, sudoable=True):
        """run a command on the remote host."""

        if self.is_container:
            # NOTE(hwoarang): the shlex_quote method is necessary here because
            # we need to properly quote the cmd as it's being passed as argument
            # to the -c su option. The Ansible ssh class has already
            # quoted the command of the _executable_ (ie /bin/bash -c "$cmd").
            # However, we also need to quote the executable itself because the
            # entire command is being passed to the su process. This produces
            # a somewhat ugly output with too many quotes in a row but we can't
            # do much since we are effectively passing a command to a command
            # to a command etc... It's somewhat ugly but maybe it can be
            # improved somehow...
            _pad = 'lxc-attach --clear-env --name %s' % self.container_name
            cmd = '%s %s -- su - %s -c %s' % (
                self._play_context.become_method,
                _pad,
                self.container_user,
                shlex_quote(cmd)
            )

        return super(Connection, self).exec_command(cmd, in_data, sudoable)

    def _container_check(self):
        if self.container_name is not None:
            SSH.display.vvv(u'container_name: "%s"' % self.container_name)
            if self.physical_host is not None:
                SSH.display.vvv(
                    u'physical_host: "%s"' % self.physical_host
                )
                if self.container_name != self.physical_host and \
                   self.container_name != self.host:
                    SSH.display.vvv(u'Container confirmed')
                    return True

        return False

    def _pid_lookup(self, subdir=None):
        """Lookup the container pid return padding.

        The container pid path will be set and returned to the
        function. If this is a new lookup, the method will run
        a lookup command and set the "self.container_pid" variable
        so that a container lookup is not required on a subsequent
        command within the same task.
        """
        pid_path = """/proc/%s"""
        if not subdir:
            subdir = 'root'

        if not self.container_pid:
            ssh_executable = self.get_option('ssh_executable')
            lookup_command = (u"lxc-info -Hpn '%s'" % self.container_name)
            args = (ssh_executable, 'ssh', self.host, lookup_command)
            returncode, stdout, _ = self._run(
                self._build_command(*args),
                in_data=None,
                sudoable=False
            )
            self.container_pid = stdout.strip()
            pid_path = os.path.join(
                pid_path % SSH.to_text(self.container_pid),
                subdir
            )
            return returncode, pid_path
        else:
            return 0, os.path.join(
                pid_path % SSH.to_text(self.container_pid),
                subdir
            )

    def _container_path_pad(self, path):
        returncode, pid_path = self._pid_lookup()
        if returncode == 0:
            pad = os.path.join(
                pid_path,
                path.lstrip(os.sep)
            )
            SSH.display.vvv(
                u'The path has been padded with the following to support a'
                u' container rootfs: [ %s ]' % pad
            )
            return pad
        else:
            return path

    def fetch_file(self, in_path, out_path):
        """fetch a file from remote to local."""
        if self.is_container:
            in_path = self._container_path_pad(path=in_path)

        return super(Connection, self).fetch_file(in_path, out_path)

    def put_file(self, in_path, out_path):
        """transfer a file from local to remote."""
        _out_path = os.path.expanduser(out_path)
        if self.is_container:
            _out_path = self._container_path_pad(path=_out_path)

        res = super(Connection, self).put_file(in_path, _out_path)

        # NOTE(mnaser): If we're running without a container, we break out
        #               here to avoid the extra round-trip for the unnecessary
        #               chown.
        if not self.is_container:
            return res

        # NOTE(pabelanger): Because we put_file as remote_user, it is possible
        # that user doesn't exist inside the container, so use the root user to
        # chown the file to container_user.
        if self.container_user != self._play_context.remote_user:
            _user = self.container_user
            self.container_user = 'root'
            self.exec_command('chown %s %s' % (_user, out_path))
            self.container_user = _user
