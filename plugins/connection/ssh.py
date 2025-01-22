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
      host:
          description: Hostname/ip to connect to.
          default: inventory_hostname
          vars:
               - name: inventory_hostname
               - name: ansible_host
               - name: ansible_ssh_host
               - name: delegated_vars['ansible_host']
               - name: delegated_vars['ansible_ssh_host']
      host_key_checking:
          description: Determines if ssh should check host keys
          type: boolean
          ini:
              - section: defaults
                key: 'host_key_checking'
              - section: ssh_connection
                key: 'host_key_checking'
                version_added: '2.5'
          env:
              - name: ANSIBLE_HOST_KEY_CHECKING
              - name: ANSIBLE_SSH_HOST_KEY_CHECKING
                version_added: '2.5'
          vars:
              - name: ansible_host_key_checking
                version_added: '2.5'
              - name: ansible_ssh_host_key_checking
                version_added: '2.5'
      password:
          description: Authentication password for the C(remote_user). Can be supplied as CLI option.
          vars:
              - name: ansible_password
              - name: ansible_ssh_pass
      sshpass_prompt:
          description:
              - Password prompt that sshpass should search for. Supported by sshpass 1.06 and up.
              - Defaults to C(Enter PIN for) when pkcs11_provider is set.
          default: ''
          type: string
          ini:
              - section: 'ssh_connection'
                key: 'sshpass_prompt'
          env:
              - name: ANSIBLE_SSHPASS_PROMPT
          vars:
              - name: ansible_sshpass_prompt
          version_added: '2.10'
      ssh_args:
          description: Arguments to pass to all ssh cli tools
          default: '-C -o ControlMaster=auto -o ControlPersist=60s'
          ini:
              - section: 'ssh_connection'
                key: 'ssh_args'
          env:
              - name: ANSIBLE_SSH_ARGS
      ssh_common_args:
          description: Common extra args for all ssh CLI tools
          vars:
              - name: ansible_ssh_common_args
      ssh_executable:
          default: ssh
          description:
            - This defines the location of the ssh binary. It defaults to `ssh` which will use the first ssh binary available in $PATH.
            - This option is usually not required, it might be useful when access to system ssh is restricted,
              or when using ssh wrappers to connect to remote hosts.
          env: [{name: ANSIBLE_SSH_EXECUTABLE}]
          ini:
          - {key: ssh_executable, section: ssh_connection}
          yaml: {key: ssh_connection.ssh_executable}
          #const: ANSIBLE_SSH_EXECUTABLE
          version_added: "2.2"
      scp_extra_args:
          description: Extra exclusive to the 'scp' CLI
          vars:
              - name: ansible_scp_extra_args
      sftp_extra_args:
          description: Extra exclusive to the 'sftp' CLI
          vars:
              - name: ansible_sftp_extra_args
      ssh_extra_args:
          description: Extra exclusive to the 'ssh' CLI
          vars:
              - name: ansible_ssh_extra_args
      reconnection_retries:
          # constant: ANSIBLE_SSH_RETRIES
          description: Number of attempts to connect.
          default: 3
          type: integer
          env:
            - name: ANSIBLE_SSH_RETRIES
          ini:
            - section: connection
              key: retries
            - section: ssh_connection
              key: retries
      port:
          description: Remote port to connect to.
          type: int
          default: 22
          ini:
            - section: defaults
              key: remote_port
          env:
            - name: ANSIBLE_REMOTE_PORT
          vars:
            - name: ansible_port
            - name: ansible_ssh_port
      remote_user:
          description:
              - User name with which to login to the remote server, normally set by the remote_user keyword.
              - If no user is supplied, Ansible will let the ssh client binary choose the user as it normally
          ini:
            - section: defaults
              key: remote_user
          env:
            - name: ANSIBLE_REMOTE_USER
          vars:
            - name: ansible_user
            - name: ansible_ssh_user
      pipelining:
          default: ANSIBLE_PIPELINING
          description:
            - Pipelining reduces the number of SSH operations required to execute a module on the remote server,
              by executing many Ansible modules without actual file transfer.
            - This can result in a very significant performance improvement when enabled.
            - However this conflicts with privilege escalation (become).
              For example, when using sudo operations you must first disable 'requiretty' in the sudoers file for the target hosts,
              which is why this feature is disabled by default.
          env:
            - name: ANSIBLE_PIPELINING
            #- name: ANSIBLE_SSH_PIPELINING
          ini:
            - section: defaults
              key: pipelining
            #- section: ssh_connection
            #  key: pipelining
          type: boolean
          vars:
            - name: ansible_pipelining
            - name: ansible_ssh_pipelining
      private_key_file:
          description:
              - Path to private key file to use for authentication
          ini:
            - section: defaults
              key: private_key_file
          env:
            - name: ANSIBLE_PRIVATE_KEY_FILE
          vars:
            - name: ansible_private_key_file
            - name: ansible_ssh_private_key_file
      control_path:
        default: null
        description:
          - This is the location to save ssh's ControlPath sockets, it uses ssh's variable substitution.
          - Since 2.3, if null, ansible will generate a unique hash. Use `%(directory)s` to indicate where to use the control dir path setting.
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH
        ini:
          - key: control_path
            section: ssh_connection
      control_path_dir:
        default: ~/.ansible/cp
        description:
          - This sets the directory to use for ssh control path if the control path setting is null.
          - Also, provides the `%(directory)s` variable for the control path setting.
        env:
          - name: ANSIBLE_SSH_CONTROL_PATH_DIR
        ini:
          - section: ssh_connection
            key: control_path_dir
      sftp_batch_mode:
        default: True
        description: 'TODO: write it'
        env: [{name: ANSIBLE_SFTP_BATCH_MODE}]
        ini:
        - {key: sftp_batch_mode, section: ssh_connection}
        type: boolean
      scp_if_ssh:
        default: smart
        description:
          - "Preferred method to use when transferring files over ssh"
          - When set to smart, Ansible will try them until one succeeds or they all fail
          - If set to True, it will force 'scp', if False it will use 'sftp'
        env: [{name: ANSIBLE_SCP_IF_SSH}]
        ini:
        - {key: scp_if_ssh, section: ssh_connection}
      use_tty:
        version_added: '2.5'
        default: True
        description: add -tt to ssh commands to force tty allocation
        env: [{name: ANSIBLE_SSH_USETTY}]
        ini:
        - {key: usetty, section: ssh_connection}
        type: boolean
        yaml: {key: connection.usetty}
      sftp_executable:
        default: sftp
        description:
          - This defines the location of the sftp binary. It defaults to `sftp` which will use the first binary available in $PATH.
        env: [{name: ANSIBLE_SFTP_EXECUTABLE}]
        ini:
        - {key: sftp_executable, section: ssh_connection}
        version_added: "2.6"
      scp_executable:
        default: scp
        description:
          - This defines the location of the scp binary. It defaults to `scp` which will use the first binary available in $PATH.
        env: [{name: ANSIBLE_SCP_EXECUTABLE}]
        ini:
        - {key: scp_executable, section: ssh_connection}
        version_added: "2.6"
      ssh_transfer_method:
        description: Preferred method to use when transferring files over ssh
        choices:
              sftp: This is the most reliable way to copy things with SSH.
              scp: Deprecated in OpenSSH. For OpenSSH >=9.0 you must add an additional option to enable scp C(scp_extra_args="-O").
              piped: Creates an SSH pipe with C(dd) on either side to copy the data.
              smart: Tries each method in order (sftp > scp > piped), until one succeeds or they all fail.
        default: smart
        type: string
        env: [{name: ANSIBLE_SSH_TRANSFER_METHOD}]
        ini:
            - {key: transfer_method, section: ssh_connection}
        vars:
            - name: ansible_ssh_transfer_method
              version_added: '2.12'
      timeout:
        default: 10
        description:
            - This is the default amount of time we will wait while establishing an ssh connection
            - It also controls how long we can wait to access reading the connection once established (select on the socket)
        env:
            - name: ANSIBLE_TIMEOUT
            - name: ANSIBLE_SSH_TIMEOUT
              version_added: '2.11'
        ini:
            - key: timeout
              section: defaults
            - key: timeout
              section: ssh_connection
              version_added: '2.11'
        vars:
          - name: ansible_ssh_timeout
            version_added: '2.11'
        cli:
          - name: timeout
        type: integer
      pkcs11_provider:
        version_added: '2.12'
        default: ""
        description:
          - "PKCS11 SmartCard provider such as opensc, example: /usr/local/lib/opensc-pkcs11.so"
          - Requires sshpass version 1.06+, sshpass must support the -P option.
        env: [{name: ANSIBLE_PKCS11_PROVIDER}]
        ini:
          - {key: pkcs11_provider, section: ssh_connection}
        vars:
          - name: ansible_ssh_pkcs11_provider
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
