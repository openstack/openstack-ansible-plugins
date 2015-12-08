plugins Docs
============

These are the plugins the OpenStack-Ansible deployment project relies on.
The plugins can be added to any openstack deployment by quite simply cloning
this repository into your plugin and library source and setting up the
``ansible.cfg`` file to point at them as additional plugins for your project.


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

The Ansible role requirement file can be used to overload the ``ansible-galaxy``
command to automatically fetch the plugins for you in a given project. To do this 
add the following lines to your ``ansible-role-requirements.yml`` file.

.. code-block:: yaml

    - name: plugins
      src: https://github.com/openstack/openstack-ansible-plugins
      path: /etc/ansible
      scm: git
      version: master

