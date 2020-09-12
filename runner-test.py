from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import json
from pprint import pprint
import time

# Import and register custom runner
from nornir.core.plugins.runners import RunnersPluginRegister
from custom_runners import runner_as_completed, runner_as_completed_tqdm
RunnersPluginRegister.register("my_runner", runner_as_completed_tqdm)


def show_version(task):
    cmd = 'show version | inc uptime'
    result = task.run(task=netmiko_send_command, name='cmd', command_string=cmd)


def main():
    nr = InitNornir(config_file='config-runner.yaml')
    agg_result = nr.run(task=show_version)
    #print_result(results)
    for hostname, multi_result in agg_result.items():
        if not multi_result.failed:
            print(multi_result[1].result)


if __name__ == '__main__':
    main()


""" Notes

#Install
pip install --upgrade nornir
pip install nornir_utils
pip install nornir_netmiko

#config-runner.yaml
---
runner:
 plugin: my_runner
 options:
  num_workers: 4

inventory:
 plugin: SimpleInventory
 options:
  host_file: "inventory/hosts.yaml"
  group_file: "inventory/groups.yaml"
  defaults_file: "inventory/defaults.yaml"

"""
