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
#
# (c) 2017, Jean-Philippe Evrard <jean-philippe.evrard@rackspace.co.uk>

# Take a path to a debian mirror release file, and outputs a dict with
# package names, each of the packages holding the following:
# - package version
# - checksums
# - Relative location to pool folder
#
# example:
# get_url:
#   url: http://rpc-repo.rackspace.com/apt-mirror/integrated/dists/r14.0.0rc1-trusty/main/binary-amd64/Packages
#   dest: /tmp/trusty-amd64-Packages
# debug:
#   var: item
# with_packages_file:
#    - /tmp/trusty-amd64-Packages

import os

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError

IMPORTANT_FIELDS = ['Version', 'Filename', 'MD5sum', 'SHA1', 'SHA256']

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

def parse_fields(line):
    for field in IMPORTANT_FIELDS:
        if line.startswith(field + ":"):
            return (field, line.split(":")[1].strip())


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        ret = []
        for term in terms:
            pkg_details = {}
            with open(term, 'r') as f:
                for line in f:
                    #non empty line means pkg data
                    if line.strip():
                        if line.startswith('Package:'):
                            currentpkg = line.split(":")[1].strip()
                            pkg_details[currentpkg] = {}
                        elif line.startswith('Provides:'):
                            pkg_details[line.split(":")[1].strip()] = pkg_details[currentpkg]
                        else:
                            # Now doing package data
                            parsed = parse_fields(line)
                            if parsed:
                                pkg_details[currentpkg][parsed[0]] = parsed[1]
                    else:
                        currentpkg=""
            ret.append(pkg_details)
        return ret

# For debug purposes
if __name__ == '__main__':
    import sys
    import json
    print(json.dumps(LookupModule().run(terms=sys.argv[1:]), indent=4, sort_keys=True))
