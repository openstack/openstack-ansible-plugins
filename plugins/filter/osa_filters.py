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
#
# (c) 2015, Kevin Carter <kevin.carter@rackspace.com>

import hashlib
import os
import re

from ansible import errors
from ansible.utils.display import Display
from jinja2 import pass_environment
from jinja2 import runtime
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

"""Filter usage:

Simple filters that may be useful from within the stack
"""


def _deprecated(new_var, old_var=None, old_var_name=None,
                new_var_name=None, removed_in=None, fatal=False):
    """Provide a deprecation warning on deprecated variables.

    This filter will return the old_var value if defined along with a
    deprecation warning that will inform the user that the old variable
    should no longer be used.

    In order to use this filter the old and new variable names must be provided
    to the filter as a string which is used to render the warning message. The
    removed_in option is used to give a date or release name where the old
    option will be removed. Optionally, if fatal is set to True, the filter
    will raise an exception if the old variable is used.

    USAGE: {{ new_var | deprecated(old_var,
                                   "old_var_name",
                                   "new_var_name",
                                   "removed_in",
                                   false) }}

    :param new_var: ``object``
    :param old_var: ``object``
    :param old_var_name: ``str``
    :param new_var_name: ``str``
    :param removed_in: ``str``
    :param fatal: ``bol``
    """
    _usage = (
        'USAGE: '
        '{{ new_var | deprecated(old_var=old_var, old_var_name="old_var_name",'
        ' new_var_name="new_var_name", removed_in="removed_in",'
        ' fatal=false) }}'
    )

    if not old_var_name:
        raise errors.AnsibleUndefinedVariable(
            'To use this filter you must provide the "old_var_name" option'
            ' with the string name of the old variable that will be'
            ' replaced. ' + _usage
        )
    if not new_var_name:
        raise errors.AnsibleUndefinedVariable(
            'To use this filter you must provide the "new_var_name" option'
            ' with the string name of the new variable that will replace the'
            ' deprecated one. ' + _usage
        )
    if not removed_in:
        raise errors.AnsibleUndefinedVariable(
            'To use this filter you must provide the "removed_in" option with'
            ' the string name of the release where the old_var will be'
            ' removed. ' + _usage
        )

    # If old_var is undefined or has a None value return the new_var value
    if isinstance(old_var, runtime.Undefined) or not old_var:
        return new_var

    display = Display()
    message = (
        'Deprecated Option provided: Deprecated variable: "%(old)s", Removal'
        ' timeframe: "%(removed_in)s", Future usage: "%(new)s"'
        % {'old': old_var_name, 'new': new_var_name, 'removed_in': removed_in}
    )

    if str(fatal).lower() in ['yes', 'true']:
        message = 'Fatally %s' % message
        raise RuntimeError(message)
    else:
        display.warning(message)
        return old_var


def _pip_requirement_split(requirement):
    version_descriptors = "(>=|<=|>|<|==|~=|!=)"
    requirement = requirement.split(';')
    requirement_info = re.split(r'%s\s*' % version_descriptors, requirement[0])
    name = requirement_info[0]
    marker = None
    if len(requirement) > 1:
        marker = requirement[1]
    versions = None
    if len(requirement_info) > 1:
        versions = requirement_info[1]

    return name, versions, marker


def _lower_set_lists(list_one, list_two):

    _list_one = set([i.lower() for i in list_one])
    _list_two = set([i.lower() for i in list_two])
    return _list_one, _list_two


def string_2_int(string):
    """Return the an integer from a string.

    The string is hashed, converted to a base36 int, and the modulo of 10240
    is returned.

    :param string: string to retrieve an int from
    :type string: ``str``
    :returns: ``int``
    """
    # Try to encode utf-8 else pass
    try:
        string = string.encode('utf-8')
    except AttributeError:
        pass
    hashed_name = hashlib.sha256(string).hexdigest()
    return int(hashed_name, 36) % 10240


def splitlines(string_with_lines):
    """Return a ``list`` from a string with lines."""

    return string_with_lines.splitlines()


@pass_environment
def osa_rejectattr(environment, data, attribute, *args, **kwargs):
    """A wrapper for rejectattr that doesn't fail on missing attributes.

    If an element is missing the attribute, it is kept. This is to preserve
    the behavior of rejectattr before ansible-core 2.19.

    This filter leverages the original rejectattr logic for elements that
    do have the attribute.
    """
    # Resolve the test name and arguments. Default is 'defined' as per Jinja2.
    test_name = args[0] if args else 'defined'
    test_args = args[1:]

    result = []
    for item in data:
        # Check if the attribute is present on the item.
        if (isinstance(item, dict) and attribute in item) or \
           (not isinstance(item, dict) and hasattr(item, attribute)):

            if isinstance(item, dict):
                val = item.get(attribute)
            else:
                val = getattr(item, attribute)

            # Apply the test using the environment.
            # rejectattr logic: if test(value) is True, the item is REJECTED.
            if not environment.call_test(test_name, val,
                                         args=test_args, kwargs=kwargs):
                result.append(item)
        else:
            result.append(item)

    return result


class FilterModule(object):
    """Ansible jinja2 filters."""

    @staticmethod
    def filters():
        return {
            'string_2_int': string_2_int,
            'splitlines': splitlines,
            'deprecated': _deprecated,
            'rejectattr': osa_rejectattr
        }
