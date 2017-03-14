# (c) 2017, Jean-Philippe Evrard <jean-philippe.evrard@rackspace.co.uk>
#
# Copyright 2017, Rackspace US, Inc.
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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


from ansible.parsing.dataloader import DataLoader
from ansible.utils.vars import merge_hash


def vars_files_loading(folder, name, matched=False):
    """ Load files recursively and sort them
    """
    files = []
    try:
        candidates = [os.path.join(folder, f) for f in os.listdir(folder)]
    except OSError:
        return files
    for f in candidates:
        if os.path.basename(f) in [name, name + ".yml", name + ".yaml"]
        or matched:
            if os.path.isfile(f):
                files.append(f)
            elif os.path.isdir(f):
                files.extend(vars_files_loading(f, name, matched=True))
    return sorted(files)


class VarsModule(object):
    """
    Loads variables for groups and/or hosts
    """

    def __init__(self, inventory):
        """ constructor """

        self.inventory = inventory
        self.inventory_basedir = inventory.basedir()
        self.grp_vars_string = os.environ.get(
            'GROUP_VARS_PATH', '/etc/openstack_deploy/group_vars')
        self.grp_vars_folders = self.grp_vars_string.split(":")
        self.host_vars_string = os.environ.get(
            'HOST_VARS_PATH', '/etc/openstack_deploy/host_vars')
        self.host_vars_folders = self.host_vars_string.split(":")

    def run(self, host, vault_password=None):
        """ This function is only used for backwards compatibility with ansible1.
            We don't need to handle this case.
        """
        return {}

    def get_host_vars(self, host, vault_password=None):
        """ Get host specific variables. """
        resulting_host_vars = {}
        var_files = []

        for host_var_folder in self.host_vars_folders:
            var_files.extend(vars_files_loading(host_var_folder, host.name))

        _dataloader = DataLoader()
        _dataloader.set_vault_password(vault_password)
        for filename in var_files:
            display.vvvvv(
                "Hostname {}: Loading var file {}".format(host.name, filename))
            data = _dataloader.load_from_file(filename)
            if data is not None:
                resulting_host_vars = merge_hash(resulting_host_vars, data)
        return resulting_host_vars

    def get_group_vars(self, group, vault_password=None):
        """ Get group specific variables. """

        resulting_group_vars = {}
        var_files = []

        for grp_var_folder in self.grp_vars_folders:
            var_files.extend(vars_files_loading(grp_var_folder, group.name))

        _dataloader = DataLoader()
        _dataloader.set_vault_password(vault_password)
        for filename in var_files:
            display.vvvvv(
                "Group {}: Loading var file {}".format(group.name, filename))
            data = _dataloader.load_from_file(filename)
            if data is not None:
                resulting_group_vars = merge_hash(resulting_group_vars, data)
        return resulting_group_vars
