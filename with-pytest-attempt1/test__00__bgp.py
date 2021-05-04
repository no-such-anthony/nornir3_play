import pytest
from nornir_netmiko import netmiko_send_command
from genie.utils import Dq


def bgp_name_test(item):

    return f"{item['device_name']} bgp neighbor {item['neighbor']}"


def pytest_generate_tests(metafunc):

    nr = metafunc.config._nr

    # get bgp output and parameterize
    output = nr.run(task=netmiko_send_command,
                    command_string='show bgp ipv4 unicast summary',
                    use_genie=True,
                    enable=True)

    param = []
    for device_name, result in output.items():
        nr.inventory.hosts[device_name]['show_bgp_ipv4_unicast_summary'] = result[0].result
        if result[0].failed:
            print(f'\n{device_name} failed with {result[0].exception}.')
        else:    
            for neighbor in Dq(result[0].result).get_values('neighbor'):
                param.append({ 'device_name': device_name,
                               'neighbor': neighbor
                               })

    metafunc.parametrize('neighbor',
                          param,
                          ids=bgp_name_test
                          )


# per bgp neighbor tests
def test_bgp_summary(nr, neighbor):
    
    host = nr.inventory.hosts[neighbor['device_name']]
    bgp_ipv4_unicast_summary = host.data['show_bgp_ipv4_unicast_summary']
    state_pfxrcd = Dq(bgp_ipv4_unicast_summary).contains(neighbor['neighbor']).get_values('state_pfxrcd')[0]

    if state_pfxrcd in ['Idle','Active']:
        pytest.fail(f'Inactive neighbor.')

    elif state_pfxrcd == 'Idle (Admin)':
        pytest.fail(f'Neighbor administratively shutdown.')

    elif state_pfxrcd == '0':
        pytest.fail(f'Neighbor up, but no prefixes received.')
       
    # BGP up and prefixes being received!  Well, after a few more checks, but this will for now :)
    return True
    
