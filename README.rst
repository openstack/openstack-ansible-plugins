OpenStack-Ansible Plugins
=========================

These are the plugins the OpenStack-Ansible deployment project relies on. The
plugins can be added to any Ansible project by simply cloning this repository
and setting up the ``ansible.cfg`` file to point at them as additional plugins
for your project.

Actions
-------

This project provides the Ansible modules:

 * config_template
 * dist_sort
 * glance
 * keystone
 * memcached
 * name2int
 * neutron
 * provider_networks

Filters
-------

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
-------

This project provides the lookup:

 * with_py_pkgs

Callbacks
---------

This project provides an Ansible callback that will report
task profiling timings


Example ansible.cfg file
------------------------

.. code-block:: ini

    [defaults]
    lookup_plugins = /etc/ansible/plugins/lookups
    filter_plugins = /etc/ansible/plugins/filters
    action_plugins = /etc/ansible/plugins/actions
    library = /etc/ansible/plugins/library


Example role requirement overload for automatic plugin download
---------------------------------------------------------------

The Ansible role requirement file can be used to overload the ``ansible-
galaxy`` command to automatically fetch the plugins for you in a given
project. To do this add the following lines to your ``ansible-role-
requirements.yml`` file.

.. code-block:: yaml

    - name: plugins
      src: https://github.com/openstack/openstack-ansible-plugins
      path: /etc/ansible
      scm: git
      version: master
