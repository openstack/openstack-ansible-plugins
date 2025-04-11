import importlib
import yaml
SSH = importlib.import_module('ansible.plugins.connection.ssh')

# Extract the options key from the builtin ansible ssh plugin
# DOCUMENTATION variable, and construct a documentation fragment
# that can be re-used in other modules derived from the builtin
# ssh plugin.
class ModuleDocFragment(object):
    DOCUMENTATION = yaml.dump({
        "options": yaml.safe_load(SSH.DOCUMENTATION)["options"]
    })
