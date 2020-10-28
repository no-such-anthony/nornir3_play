from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
import ruamel.yaml

from nornir.core.inventory import Inventory, Hosts, Host
from nornir.plugins.inventory.simple import _get_inventory_element


def show_version(task):
    cmd = 'show version | inc uptime'
    result = task.run(task=netmiko_send_command, name='cmd', command_string=cmd)


def getHosts():
    #whatever you need to do to return the hosts dict
    yml = ruamel.yaml.YAML(typ="safe")
    hosts_file = "inventory/hosts2.yaml"
    with open(hosts_file, "r") as f:
        hosts_dict = yml.load(f)
    return hosts_dict


def buildHosts(hosts_dict):
    #remember no groups or defaults
    hosts = Hosts()
    for n, h in hosts_dict.items():
        h.pop('groups', None)
        hosts[n] = _get_inventory_element(Host, h, n, {})
    return hosts


#you will still need a default dictionary to load, but overwrite after
nr = InitNornir(config_file='config.yaml',)
print(len(nr.inventory.hosts))

setattr(nr,'inventory',Inventory(hosts=buildHosts(getHosts()), groups={}, defaults={}))
print(len(nr.inventory.hosts))

agg_result = nr.run(task=show_version)
for hostname, multi_result in agg_result.items():
    print(hostname, multi_result[1].result)
