=======
Lookups
=======

py_pkgs
~~~~~~~
The ``py_pkgs`` lookup crawls a given list of directories to parse variables
and generate lists of Python packages, git repo information and Ansible group
memberships which is used within OpenStack-Ansible's repo_build role to build
wheels and virtual environments.

Files and paths containing the following strings are evaluated:
 - test-requirements.txt
 - dev-requirements.txt
 - requirements.txt
 - global-requirements.txt
 - global-requirement-pins.txt
 - /defaults/
 - /vars/
 - /user_*

Variables parsed within any evaluated files include:
 - service_pip_dependencies
 - pip_common_packages
 - pip_container_packages
 - pip_packages

Example
-------

.. code-block:: yaml

   - name: Load local packages
     debug:
       msg: "Loading Packages"
     with_py_pkgs: "{{ pkg_locations }}"
     register: local_packages
     vars:
       pkg_locations:
         - "/etc/ansible/roles/os_nova"
   # => {
   #    "packages": [
   #        "httplib2",
   #        "keystonemiddleware",
   #        "libvirt-python",
   #        "nova",
   #        "nova-lxd",
   #        "nova-powervm",
   #        "pyasn1-modules",
   #        "pycrypto",
   #        "pylxd",
   #        "pymysql",
   #        "python-ironicclient",
   #        "python-keystoneclient",
   #        "python-memcached",
   #        "python-novaclient",
   #        "virtualenv",
   #        "websockify"
   #    ],
   #    "remote_package_parts": [
   #        {
   #            "egg_name": "nova",
   #            "fragment": null,
   #            "name": "nova",
   #            "original":
   #               "git+https://git.openstack.org/openstack/nova@stable/newton#egg=nova&gitname=nova&projectgroup=all",
   #            "project_group": "all",
   #            "url": "https://git.openstack.org/openstack/nova",
   #            "version": "stable/newton"
   #        },
   #        {
   #            "egg_name": "nova_lxd",
   #            "fragment": null,
   #            "name": "nova-lxd",
   #            "original":
   #               "git+https://git.openstack.org/openstack/nova-lxd@stable/newton#egg=nova_lxd&gitname=nova-lxd&projectgroup=all",
   #            "project_group": "all",
   #            "url": "https://git.openstack.org/openstack/nova-lxd",
   #            "version": "stable/newton"
   #        },
   #        {
   #            "egg_name": "novnc",
   #            "fragment": null,
   #            "name": "novnc",
   #            "original":
   #               "git+https://github.com/kanaka/novnc@master#egg=novnc&gitname=novnc&projectgroup=all",
   #            "project_group": "all",
   #            "url": "https://github.com/kanaka/novnc",
   #            "version": "master"
   #        },
   #        {
   #            "egg_name": "spice_html5",
   #            "fragment": null,
   #            "name": "spice-html5",
   #            "original":
   #               "git+https://github.com/SPICE/spice-html5@master#egg=spice_html5&gitname=spice-html5&projectgroup=all",
   #            "project_group": "all",
   #            "url": "https://github.com/SPICE/spice-html5",
   #            "version": "master"
   #        }
   #    ],
   #    "remote_packages": [
   #        "git+https://git.openstack.org/openstack/nova-lxd@stable/newton#egg=nova_lxd&gitname=nova-lxd&projectgroup=all",
   #        "git+https://git.openstack.org/openstack/nova@stable/newton#egg=nova&gitname=nova&projectgroup=all",
   #        "git+https://github.com/SPICE/spice-html5@master#egg=spice_html5&gitname=spice-html5&projectgroup=all",
   #        "git+https://github.com/kanaka/novnc@master#egg=novnc&gitname=novnc&projectgroup=all"
   #    ],
   #    "role_packages": {
   #        "os_nova": [
   #            "httplib2",
   #            "keystonemiddleware",
   #            "libvirt-python",
   #            "nova",
   #            "nova-lxd",
   #            "nova-powervm",
   #            "pyasn1-modules",
   #            "pycrypto",
   #            "pylxd",
   #            "pymysql",
   #            "python-ironicclient",
   #            "python-keystoneclient",
   #            "python-memcached",
   #            "python-novaclient",
   #            "virtualenv",
   #            "websockify"
   #        ]
   #    },
   #    "role_project_groups": {
   #        "os_nova": "nova_all"
   #    },
   #    "role_requirement_files": {},
   #    "role_requirements": {
   #        "os_nova": {
   #            "nova_compute_ironic_pip_packages": [
   #                "python-ironicclient"
   #            ],
   #            "nova_compute_lxd_pip_packages": [
   #                "nova-lxd",
   #                "pylxd"
   #            ],
   #            "nova_compute_pip_packages": [
   #                "libvirt-python"
   #            ],
   #            "nova_compute_powervm_pip_packages": [
   #                "nova-powervm",
   #                "pyasn1-modules"
   #            ],
   #            "nova_novnc_pip_packages": [
   #                "websockify"
   #            ],
   #            "nova_pip_packages": [
   #                "keystonemiddleware",
   #                "nova",
   #                "pycrypto",
   #                "pymysql",
   #                "python-keystoneclient",
   #                "python-memcached",
   #                "python-novaclient"
   #            ],
   #            "nova_requires_pip_packages": [
   #                "httplib2",
   #                "python-keystoneclient",
   #                "virtualenv",
   #            ],
   #            "project_group": "nova_all"
   #        }
   #    }
