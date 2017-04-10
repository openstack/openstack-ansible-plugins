#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
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

set -xeu

source /etc/os-release || source /usr/lib/os-release

install_pkg_deps() {
    pkg_deps="git"

    case ${ID,,} in
        *suse*) pkg_mgr_cmd="zypper -n in" ;;
        centos|rhel) pkg_mgr_cmd="yum install -y" ;;
        fedora) pkg_mgr_cmd="dnf -y install" ;;
        ubuntu|debian) pkg_mgr_cmd="apt-get install -y" ;;
        *) echo "unsupported distribution: ${ID,,}"; exit 1 ;;
    esac

    eval sudo $pkg_mgr_cmd $pkg_deps
}

git_clone_repo() {
    if [[ ! -d tests/common ]]; then
        git clone https://git.openstack.org/openstack/openstack-ansible-tests tests/common
    fi
}

install_pkg_deps

git_clone_repo

# start executing the main test script
source tests/common/run_tests.sh

# vim: set ts=4 sw=4 expandtab:
