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

import imp
import os

# NOTICE(cloudnull): The connection plugin imported using the full path to the
#                    file because the ssh connection plugin is not importable.
import ansible.plugins.connection as conn
SSH = imp.load_source(
    'ssh',
    os.path.join(os.path.dirname(conn.__file__), 'ssh.py')
)

class Connection(SSH.Connection):
    """Transport options for LXC containers.

    This transport option makes the assumption that the playbook context has
    vars within it that contain "physical_host" which is the machine running a
    given container and "container_name" which is the actual name of the
    container. These options can be added into the playbook via vars set as
    attributes or though the modification of the a given execution strategy to
    set the attributes accordingly.

    This plugin operates exactly the same way as the standard SSH plugin but
    will pad pathing or add command syntax for lxc containers when a container
    is detected at runtime.
    """

    transport = 'ssh'

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.vars = self._play_context._attributes['vars']
        self.container_name = self.vars.get('container_name')
        self.physical_host = self.vars.get('physical_host')
        self.physical_hostname = self.vars.get('physical_hostname')
        if self._container_check():
            self.host = self._play_context.remote_addr = self.physical_host

    def _exec_command(self, cmd, in_data=None, sudoable=True):
        """run a command on the remote host."""
        if self._container_check():
            # Remote user is normally set, but if it isn't, then default to 'root'
            container_user = 'root'
            if self._play_context.remote_user:
                container_user = SSH.to_bytes(self._play_context.remote_user,
                                              errors='surrogate_or_strict')
            # NOTE(hwoarang) It is important to connect to the container
            # without inheriting the host environment as that would interfere
            # with running commands and services inside the container. However,
            # it is also important to create a sensible environment within the
            # container because certain commands and services expect some
            # enviromental variables to be set properly. The best way to do
            # that would be to execute the commands in a login shell
            lxc_command = 'lxc-attach --clear-env --name %s' % self.container_name

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
            cmd = '%s -- su - %s -c %s' % (lxc_command, container_user,
                                           SSH.shlex_quote(cmd))

        return super(Connection, self)._exec_command(cmd, in_data, sudoable)

    def _container_check(self):
        if self.container_name:
            SSH.display.vvv(u'container_name: "%s"' % self.container_name)
            if self.physical_hostname:
                SSH.display.vvv(
                    u'physical_hostname: "%s"' % self.physical_hostname
                )
                if self.container_name != self.physical_hostname:
                    SSH.display.vvv(u'Container confirmed')
                    return True

        return False

    def _container_path_pad(self, path, fake_path=False):
        args = (
            'ssh',
            self.host,
            u"lxc-info --name %s --pid | awk '/PID:/ {print $2}'"
            % self.container_name
        )
        returncode, stdout, _ = self._run(
            self._build_command(*args),
            in_data=None,
            sudoable=False
        )
        if returncode == 0:
            pad = os.path.join(
                '/proc/%s/root' % stdout.strip(),
                path.lstrip(os.sep)
            )
            SSH.display.vvv(
                u'The path has been padded with the following to support a'
                u' container rootfs: [ %s ]' % pad
            )
            return pad
        else:
            raise SSH.AnsibleError(
                u'No valid container info was found for container "%s" Please'
                u' check the state of the container.' % self.container_name
            )

    def fetch_file(self, in_path, out_path):
        """fetch a file from remote to local."""
        if self._container_check():
            in_path = self._container_path_pad(path=in_path)

        return super(Connection, self).fetch_file(in_path, out_path)

    def put_file(self, in_path, out_path):
        """transfer a file from local to remote."""
        if self._container_check():
            out_path = self._container_path_pad(path=out_path)

        return super(Connection, self).put_file(in_path, out_path)

    def close(self):
        # If we have a persistent ssh connection (ControlPersist), we can ask it
        # to stop listening. Otherwise, there's nothing to do here.
        if self._connected and self._persistent:
            cmd = self._build_command('ssh', '-O', 'stop', self.host)
            cmd = map(SSH.to_bytes, cmd)
            p = SSH.subprocess.Popen(cmd, stdin=SSH.subprocess.PIPE, stdout=SSH.subprocess.PIPE, stderr=SSH.subprocess.PIPE)
            p.communicate()

