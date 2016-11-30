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
        self.debug_tasks = []

    def v2_playbook_on_task_start(self, task, is_conditional):
        """
        Collect debug messages from tasks.

        After each task runs, this function checks to see if the task's action
        is 'debug'. If so, we collect the name of the task as well as its
        debug message here.
        """
        if task.action == 'debug':
            self.debug_tasks.append({
                'name': task.name,
                'msg': task.args['msg']
            })

    def v2_playbook_on_stats(self, stats):
        """
        Print debug messages when the playbook has finished.

        Print all of the collected debug messages (if any exist) and display
        them at the end of the Ansible task output.
        """
        if len(self.debug_tasks) > 0:
            print("DEBUG MESSAGE RECAP ".ljust(80, '*'))
        for task in self.debug_tasks:
            print("DEBUG: [{0}] ".format(task['name']).ljust(80, '*'))
            print("{0}\n".format(task['msg']))
