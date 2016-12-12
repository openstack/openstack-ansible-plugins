#!/usr/bin/env python
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
"""Callback for displaying debug messages after a playbook run."""
from collections import OrderedDict
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    Callback plugin for collecting messages from debug tasks.

    This plugin watches for debug tasks, collects the messages from those
    tasks, and displays them at the end of the playbook run.
    """

    # Ansible constants for the plugin
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'debug_message_collector'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        """Constructor for the plugin class."""
        self.debug_tasks = OrderedDict()

    def v2_runner_on_ok(self, result):
        """
        Get details from debug tasks.

        We only care about successful debug tasks. This function takes the
        debug message that is returned from the task and adds it into a
        dictionary of debug tasks. The message includes rendered template data
        if jinja2 templates were used to generate the debug output.
        """
        if result._task.action == 'debug':
            self.debug_tasks[result._task._uuid] = {
                'name': result._task.name,
                'msg': result._result['msg'],
            }

    def v2_playbook_on_stats(self, stats):
        """
        Print debug tasks at the end of the playbook run.

        Print all of the collected debug messages (if any exist) and display
        them at the end of the Ansible task output.
        """
        if len(self.debug_tasks) > 0:
            print("DEBUG MESSAGE RECAP ".ljust(80, '*'))
        for uuid, task in self.debug_tasks.items():
            print("DEBUG: [{0}] ".format(task['name']).ljust(80, '*'))
            print("{0}\n".format(task['msg']))
