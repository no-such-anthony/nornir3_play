# Custom Inventory - Reads dicts as arguments to build inventory
# copied from
# https://github.com/nornir-automation/nornir/blob/develop/nornir/plugins/inventory/simple.py
# and modified for dict input
#
# Other custom inventory examples
# https://github.com/nornir-automation/nornir3_demo/blob/master/nornir3_demo/plugins/inventory/acme.py
#
#

"""

Usage:

from nornir import InitNornir

# Custom inventory - dict format
from nornir.core.plugins.inventory import InventoryPluginRegister
from simpleDict import SimpleInventoryDict
InventoryPluginRegister.register("simpleDict", SimpleInventoryDict)
# or use whatever plugin register method you like


hosts_dict = {}
groups_dict = {}
defaults_dict = {}

# build hosts,groups, and defaults dicts however you need
# then

nr = InitNornir(config_file='config.yaml',
                inventory={
                            "plugin": "simpleDict",
                            "options": {
                                "hosts_dict" : hosts_dict,
                                "groups_dict": groups_dict,
                                "defaults_dict": defaults_dict,
                            },
                        })

print(len(nr.inventory.hosts))
"""

from nornir.plugins.inventory.simple import _get_connection_options,_get_defaults,_get_inventory_element

from nornir.core.inventory import (
    Inventory,
    Groups,
    Hosts,
    Defaults,
)


class SimpleInventoryDict:
    def __init__(
        self,
        hosts_dict: dict = {},
        groups_dict: dict = {},
        defaults_dict: dict = {},
    ) -> None:
        """
        SimpleInventoryDict is an inventory plugin that loads data from python dictionaries.
        The dicts follow the same structure as the native objects

        Args:

          host_dict: dict with hosts definition
          group_dict: dict with groups definition.
          defaults_dict: dict with defaults definition.
        """

        self.defaults_dict = defaults_dict
        self.hosts_dict = hosts_dict
        self.groups_dict = groups_dict


    def load(self) -> Inventory:

        defaults = _get_defaults(self.defaults_dict)

        hosts = Hosts()

        for n, h in self.hosts_dict.items():
            hosts[n] = _get_inventory_element(Host, h, n, defaults)

        groups = Groups()

        for n, g in self.groups_dict.items():
            groups[n] = _get_inventory_element(Group, g, n, defaults)

        for h in hosts.values():
            h.groups = ParentGroups([groups[g] for g in h.groups])

        for g in groups.values():
            g.groups = ParentGroups([groups[g] for g in g.groups])

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
