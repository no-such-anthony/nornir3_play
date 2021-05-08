from nornir import InitNornir
from nornir.core.filter import F
from genie.utils import Dq
from genie.conf.base.utils import QDict
from nornir_netmiko import netmiko_send_command


class PTNR(object):
    """ for Nornir specific config / runtime """

    def __init__(self, filt=''):
        self.nr = InitNornir(config_file="config.yaml")

        if filt:
            fd = {}
            for a in filt:
                k, v = a.split(':')
                if k.endswith('__any'):
                    v = [x.strip() for x in v.split(',')]
                fd[k] = v
            ff = F(**fd)

            self.nr = self.nr.filter(ff)


    def connection_setup(self, task):

        net_connect = task.host.get_connection("netmiko", task.nornir.config)
        
        enable = 'secret' in task.host.get_connection_parameters("netmiko").extras
        if enable:
            net_connect.enable()


    def get_conns(self):
        output = self.nr.run(task=self.connection_setup)

        self.param_conns = []
        for device_name, result in output.items():
            if result[0].failed:
                print(f'\n{device_name} failed with {result[0].exception}')
                self.param_conns.append({'device_name': device_name,'state': False})
            else:
                self.param_conns.append({'device_name': device_name,'state': True})


    def get_bgp(self):

        output = self.nr.run(task=netmiko_send_command,
                        command_string='show bgp ipv4 unicast summary',
                        use_genie=True,
                        enable=True)

        self.param_neighbor = []
        self.param_device = []
        for device_name, result in output.items():
            self.nr.inventory.hosts[device_name]['show_bgp_ipv4_unicast_summary'] = result[0].result
            if result[0].failed:
                print(f'\n{device_name} failed with {result[0].exception}')
            elif not isinstance(result[0].result, QDict):
                if '% BGP not active' in result[0].result:
                    self.param_device.append({'device_name': device_name,'state': False})
                else:
                    print(f'\n{device_name} - {result[0].result}')
            else:    
                self.param_device.append({'device_name': device_name,'state': True})
                for neighbor in Dq(result[0].result).get_values('neighbor'):
                    self.param_neighbor.append({ 'device_name': device_name,
                                'neighbor': neighbor
                                })


    def get_device_conns(self):
        return self.param_conns
    

    def get_bgp_devices(self):
        return self.param_device


    def get_bgp_neighbors(self):
        return self.param_neighbor
