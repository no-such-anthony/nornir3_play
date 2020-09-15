from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import json
from pprint import pprint
import time

# Import and register custom runner
from nornir.core.plugins.runners import RunnersPluginRegister
from custom_runners import runner_as_completed, runner_as_completed_tqdm, runner_as_completed_rich
RunnersPluginRegister.register("my_runner", runner_as_completed_rich)


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

#Alternatively, skip the runner registration and config.yaml modifications and do the following

my_runner = runner_as_completed_tqdm(num_workers=1)
nr = nr.with_runner(my_runner)
agg_result = nr.run(task=show_version)

#or

my_runner = runner_as_completed_tqdm(num_workers=1)
agg_result = nr.with_runner(my_runner).run(task=show_version)

#Links that may help me with this
https://github.com/nornir-automation/nornir3_demo/blob/master/demo/scripts/40_dc_aware_runner.py
https://github.com/nornir-automation/nornir3_demo/blob/master/nornir3_demo/plugins/runners/dc_aware.py
https://github.com/nornir-automation/nornir3_demo/blob/master/nornir3_demo/plugins/processors/rich.py
https://github.com/nornir-automation/nornir/pull/536
https://nornir.readthedocs.io/en/latest/plugins/

#Install nornir 3 then
pip install nornir_utils
pip install nornir_netmiko
pip install tqdm
pip install rich

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
