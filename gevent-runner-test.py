#!/usr/bin/env python

# Custom runner
from gevent_runner import gevent_runner
from nornir.core.plugins.runners import RunnersPluginRegister
RunnersPluginRegister.register("my_runner", gevent_runner)

from nornir import InitNornir
from nornir_netmiko import netmiko_send_command


def show_version(task):
    cmd = 'show version | inc uptime'
    result = task.run(task=netmiko_send_command, name='cmd', command_string=cmd)


def main():
    nr = InitNornir(config_file='config.yaml',
                    runner= { 'plugin':'my_runner',
                              'options': { 'num_workers': 4 }})
    agg_result = nr.run(task=show_version)

    for hostname, multi_result in agg_result.items():
        if not multi_result.failed:
            print(hostname, multi_result[1].result)


if __name__ == '__main__':
    main()

