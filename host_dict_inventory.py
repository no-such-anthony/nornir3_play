from nornir import InitNornir
import ruamel.yaml

from nornir.core.inventory import Inventory


def getHosts():
    #whatever you need to do to return the hosts dict
    yml = ruamel.yaml.YAML(typ="safe")

    hosts_file = "inventory/hosts2.yaml"
    with open(hosts_file, "r") as f:
        hosts_dict = yml.load(f)
    return hosts_dict


#you will still need a default dictionary to load, but overwrite after
nr = InitNornir(config_file='config.yaml',)
print(len(nr.inventory.hosts))

setattr(nr,'inventory',Inventory(hosts=getHosts(), groups={}, defaults={}))
print(len(nr.inventory.hosts))

for h,d in nr.inventory.hosts.items():
    print(h)
    print(d)
