=========================
OpenStack-Ansible plugins
=========================

Actions
~~~~~~~

This project provides the Ansible modules:

 * config_template
 * dist_sort
 * keystone
 * memcached
 * name2int
 * neutron
 * provider_networks

Filters
~~~~~~~

This project provides the Ansible Jinja2 filters:

 * bit_length_power_of_2
 * netloc
 * netloc_no_port
 * netorigin
 * string_2_int
 * pip_requirement_names
 * pip_constraint_update
 * splitlines
 * filtered_list
 * git_link_parse
 * git_link_parse_name
 * deprecated

Lookups
~~~~~~~

This project provides the lookup:

 * with_py_pkgs

Callbacks
~~~~~~~~~

This project provides an Ansible callback that will report
task profiling timings


Example ``ansible.cfg`` file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../examples/example.ini
   :language: yaml


Example role requirement overload for automatic plugin download
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Ansible role requirement file can be used to overload the ``ansible-
galaxy`` command to automatically fetch the plugins for you in a given
project. To do this add the following lines to your ``ansible-role-
requirements.yml`` file.

.. literalinclude:: ../../examples/playbook.yml
   :language: yaml


