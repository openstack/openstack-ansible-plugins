=======
Filters
=======

bit_length_power_of_2
~~~~~~~~~~~~~~~~~~~~~
This filter will return the smallest power of 2 greater than a given numeric
value.

.. code-block:: yaml

   {{ 1000 | bit_length_power_of_2 }}
   # => 1024

deprecated
~~~~~~~~~~
This filter will return the old_var value, if defined, along with a
deprecation warning that will inform the user that the old variable
should no longer be used.

In order to use this filter the old and new variable names must be provided
to the filter as a string which is used to render the warning message. The
removed_in option is used to give a date or release name where the old
option will be removed. Optionally, if fatal is set to True, the filter
will raise an exception if the old variable is used.

.. code-block:: yaml

   old_var: "old value"
   old_var_name: "old_var"
   new_var_name: "new_var"
   removed_in: "Next release"
   fatal_deprecations: false

   {{ new_var | deprecated(old_var,
                                  old_var_name,
                                  new_var_name,
                                  removed_in,
                                  fatal_deprecations) }}
   # WARNING => Deprecated Option provided: Deprecated variable:
   # "old_var", Removal timeframe: "Next release", Future usage:
   # "new_var"
   # => "old value"

git_link_parse
~~~~~~~~~~~~~~
This filter will return a dict containing the parts of a given git repo URL.

.. code-block:: yaml

   {{ 'https://git.openstack.org/openstack/openstack-ansible@master' |
        git_link_parse }}
   # =>
   # {
   #   "url": "https://git.openstack.org/openstack/openstack-ansible",
   #   "plugin_path": null,
   #   "version": "master",
   #   "name": "openstack-ansible",
   #   "original":
   #      "https://git.openstack.org/openstack/openstack-ansible@master"
   # }

git_link_parse_name
~~~~~~~~~~~~~~~~~~~
This filter will return the name of a given git repo URL.

.. code-block:: yaml

   {{ 'https://git.openstack.org/openstack/openstack-ansible@master' |
        git_link_parse_name }}
   # => "openstack-ansible"

filtered_list
~~~~~~~~~~~~~
This filter takes two lists as inputs. The first list will be returned to the
user after removing any duplicates found within the second list.

.. code-block:: yaml

   {{ ['a', 'b'] | filtered_list(['b', 'c']) }}
   # => [ "a" ]

netloc
~~~~~~
This filter will return the netloc from a given URL.

.. code-block:: yaml

    {{ 'https://172.29.236.100:5000/v3/auth/tokens' | netloc }}
    # => "172.29.236.100:5000"

netloc_no_port
~~~~~~~~~~~~~~
This filter will return the netloc, without a port, from a given URL.

.. code-block:: yaml

    {{ 'https://172.29.236.100:5000/v3/auth/tokens' | netloc_no_port }}
    # => "172.29.236.100"

netorigin
~~~~~~~~~
This filter will return the scheme and netloc from a given URL.

.. code-block:: yaml

    {{ 'https://172.29.236.100:5000/v3/auth/tokens' | netorigin }}
    # => "https://172.29.236.100:5000"

pip_constraint_update
~~~~~~~~~~~~~~~~~~~~~
This filter will return a merged list from a given list of pip packages and a
list of pip package constraints to a apply to that list.

.. code-block:: yaml

    pip_package_list:
      - pip==8.1.2
      - setuptools==25.1.0
      - wheel==0.29.0
    pip_package_constraint_list:
      - babel==2.3.4
      - pip==8.1.0

    {{ pip_package_list | pip_constraint_update(pip_package_constraint_list) }}
    # => [ "babel==2.3.4", "pip==8.1.0", "setuptools==25.1.0", "wheel==0.29.0" ]

pip_requirement_names
~~~~~~~~~~~~~~~~~~~~~
This filter will return of list of package names from a given list of pip
packages.

.. code-block:: yaml

   pip_package_list:
     - pip==8.1.2
     - setuptools==25.1.0
     - wheel==0.29.0

   {{ pip_package_list | pip_requirement_names }}
   # => [ "pip", "setuptools", "wheel" ]

splitlines
~~~~~~~~~~
This filter will return of list from a string with line breaks.

.. code-block:: yaml

    string_with_line_breaks: |
      a string
      with
      line
      breaks

    {{ string_with_line_breaks | splitlines }}
    # => [ "a string", "with", "line", "breaks" ]

string_2_int
~~~~~~~~~~~~
This filter will hash a given string, convert it to a base36 int, and return
the modulo of 10240.

.. code-block:: yaml

   {{ 'openstack-ansible' | string_2_int }}
   # => 3587
