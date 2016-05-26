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

import os
import sys

from distutils.version import LooseVersion
from ansible import __version__ as __ansible_version__

import requests

# This appends the sys path with the file path which is used for the
#  import of the specific verion of the config_template action plugin
#  needed based on the ansible version calling the plugin.
DIRPATH = os.path.dirname(__file__)

# NOTICE: These plugins are developed outside of OSA and can not be
#  added to the main repository due to GPL conflicts in OpenStack.
PLUGINS = {
    'v1': 'https://gist.githubusercontent.com/cliffano/9868180/raw/'
          'f32b76560b7c72cdc44e6aa0e9f46d0392f54a43/human_log.py',
    'v2': 'https://raw.githubusercontent.com/rdo-infra/weirdo/master/'
          'playbooks/library/human_log.py'
}

if DIRPATH not in sys.path:
    sys.path.append(DIRPATH)

def get_plugin(plugin, name):
    req = requests.get(plugin, stream=True)
    if req.status_code == 200:
        with open(os.path.join(DIRPATH, name), 'wb') as f:
            for chunk in req.iter_content(1024):
                f.write(chunk)
        return True
    else:
        return False

if LooseVersion(__ansible_version__) < LooseVersion("2.0"):
    if get_plugin(plugin=PLUGINS['v1'], name='_v1_human_log.py'):
        from _v1_human_log import *
else:
    if get_plugin(plugin=PLUGINS['v2'], name='_v2_human_log.py'):
        from _v2_human_log import *
