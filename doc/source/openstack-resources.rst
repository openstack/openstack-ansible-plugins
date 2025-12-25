========================
OpenStack resources role
========================

The OpenStack resources role is used to declaratively create and manage
OpenStack cloud resources. You define the resources you want in variables,
and the role ensures they are consistently provisioned and kept in the desired
state.
This role can provision and manage the following types
of OpenStack resources:

  * Identity resources: domains, projects, users, roles, endpoints, and quotas
  * Compute resources: host aggregates, flavors, flavor access rules, and
    keypairs
  * Networking resources: networks and subnets
  * Image resources: image upload, registration, and rotation

It applies these definitions as code, so environments can be bootstrapped
and maintained in a repeatable and controlled way.

Default variables
~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../roles/openstack_resources/defaults/main.yml
   :language: yaml
   :start-after: under the License.

Example of using
~~~~~~~~~~~~~~~~

For example, images and flavors can be defined in ``user_variables.yml``
and deployed with the ``openstack.osa.openstack_resources`` playbook.
The role will ensure the resources exist in OpenStack and are kept in
the desired state.

The example below uploads the AlmaLinux 10 GenericCloud image and creates two
compute flavors.

.. code-block:: yaml

   # === OpenStack Images ===
   openstack_resources_image:
     images:
       - name: almalinux-10
         url: https://repo.almalinux.org/almalinux/10/cloud/x86_64/images/AlmaLinux-10-GenericCloud-latest.x86_64.qcow2
         disk_format: qcow2
         container_format: bare
         visibility: public
         min_disk: 10
         min_ram: 1024
         state: present

   # === OpenStack Flavors ===
   openstack_resources_compute:
     flavors:
       - specs:
           - name: m1.small
             vcpus: 1
             ram: 2048        # MB
             disk: 20         # GB
             public: true
             state: present

           - name: m1.medium
             vcpus: 2
             ram: 4096
             disk: 40
             public: true
             state: present

After saving the variables file, apply the configuration with:

.. code-block:: console

   # openstack-ansible openstack.osa.openstack_resources

The role will:

* download and upload the AlmaLinux 10 image
* create (or update) the ``m1.small`` and ``m1.medium`` flavors

You can also apply only a specific type of resources by running the playbook
with the appropriate tag. For example:

.. code-block:: console

   Compute resources (flavors, keypairs)
   # openstack-ansible openstack.osa.openstack_resources --tags compute-resources

   Image resources (image upload/registration/rotation)
   # openstack-ansible openstack.osa.openstack_resources --tags image-resources

   Network resources (networks, subnets)
   # openstack-ansible openstack.osa.openstack_resources --tags network-resources
