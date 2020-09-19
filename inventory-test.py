from nornir import InitNornir

# Custom inventory - json format
from nornir.core.plugins.inventory import InventoryPluginRegister
from simpleJson import SimpleInventoryJson
InventoryPluginRegister.register("simpleJson", SimpleInventoryJson)


nr = InitNornir(config_file='config.yaml',
                inventory={
                            "plugin": "simpleJson",
                            "options": {
                                "host_file" : "inventory/hosts.json",
                                "group_file": "inventory/groups.json",
                                "defaults_file": "inventory/defaults.json"
                            },
                        })
print(len(nr.inventory.hosts))

