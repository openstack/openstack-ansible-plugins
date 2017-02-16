config_template
~~~~~~~~~~~~~~~

Synopsis
--------
Renders template files providing a create/update override interface

- The module contains the template functionality with the ability to override
  items in config, in transit, through the use of a simple dictionary without
  having to write out various temp files on target machines. The module renders
  all of the potential jinja a user could provide in both the template file and
  in the override dictionary which is ideal for deployers who may have lots of
  different configs using a similar code base.
- The module is an extension of the **copy** module and all of attributes that
  can be set there are available to be set here.

Examples
--------
.. literalinclude:: ../../../library/config_template
   :language: yaml
   :start-after: EXAMPLES = """
   :end-before: """
