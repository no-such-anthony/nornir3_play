# Custom Inventory - Reads JSON inventory files
# copied from 
# https://github.com/nornir-automation/nornir/blob/develop/nornir/plugins/inventory/simple.py
# and modified for JSON
# some may notice significant speed increase with InitNornir and large inventories
#
# for testing, to quicky convert your inventory
# alias yaml2json="python -c 'import sys, yaml, json; y=yaml.safe_load(sys.stdin.read()); print(json.dumps(y, indent=2))'"
# cat hosts.yaml | yaml2json > hosts.json
# cat groups.yaml | yaml2json > groups.json
# cat defaults.yaml | yaml2json > defaults.json
#
# Other custom inventory examples
# https://github.com/nornir-automation/nornir3_demo/blob/master/nornir3_demo/plugins/inventory/acme.py
#
#

import logging

from nornir.plugins.inventory.simple import _get_defaults,_get_inventory_element

from nornir.core.inventory import (
    Inventory,
    Groups,
    Hosts,
    Defaults,
)

import json
from json import JSONDecodeError


logger = logging.getLogger(__name__)


class SimpleInventoryJson:
    def __init__(
        self,
        host_file: str = "hosts.json",
        group_file: str = "groups.json",
        defaults_file: str = "defaults.json",
    ) -> None:
        """
        SimpleInventoryJson is an inventory plugin that loads data from JSON files.
        The JSON files follow the same structure as the native objects

        Args:

          host_file: path to file with hosts definition
          group_file: path to file with groups definition. If
                it doesn't exist it will be skipped
          defaults_file: path to file with defaults definition.
                If it doesn't exist it will be skipped
        """

        self.host_file = pathlib.Path(host_file).expanduser()
        self.group_file = pathlib.Path(group_file).expanduser()
        self.defaults_file = pathlib.Path(defaults_file).expanduser()

    def load(self) -> Inventory:

        if self.defaults_file.exists():
            with open(self.defaults_file, "r") as f:
                try:
                    defaults_dict = json.load(f)
                except JSONDecodeError:
                    defaults_dict = {}
            defaults = _get_defaults(defaults_dict)
        else:
            defaults = Defaults()

        hosts = Hosts()

        with open(self.host_file, "r") as f:
            hosts_dict = json.load(f)

        for n, h in hosts_dict.items():
            hosts[n] = _get_inventory_element(Host, h, n, defaults)

        groups = Groups()
        if self.group_file.exists():
            with open(self.group_file, "r") as f:
                try:
                    groups_dict = json.load(f)
                except JSONDecodeError:
                    groups_dict = {}
            for n, g in groups_dict.items():
                groups[n] = _get_inventory_element(Group, g, n, defaults)

            for h in hosts.values():
                h.groups = ParentGroups([groups[g] for g in h.groups])

            for g in groups.values():
                g.groups = ParentGroups([groups[g] for g in g.groups])

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
