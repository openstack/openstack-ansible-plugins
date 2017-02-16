dist_sort
~~~~~~~~~

Synopsis
--------
Deterministically sort a list to distribute the elements in the list evenly.
Based on external values such as host or static modifier. Returns a string as
named key ``sorted_list``.

- This module returns a list of servers uniquely sorted based on a index from a
  look up value location within a group. The group should be an existing
  Ansible inventory group. This will module returns the sorted list as a
  delimited string.

Examples
--------
.. literalinclude:: ../../../library/dist_sort
   :language: yaml
   :start-after: EXAMPLES = """
   :end-before: """
