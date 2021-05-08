import pytest
from nornir_netmiko import netmiko_send_command
from genie.utils import Dq
from genie.conf.base.utils import QDict


def helper_id(item):

    if isinstance(item, dict):
        return f"{item['device_name']} bgp neighbor {item['neighbor']}"


def gather_task(task):

    enable = 'secret' in task.host.get_connection_parameters("netmiko").extras
    output = task.run(task=netmiko_send_command,
                    command_string='show bgp ipv4 unicast summary',
                    use_genie=True,
                    enable=enable)


def pytest_generate_tests(metafunc):

    # get bgp output and parameterize
    output = pytest.nr.run(task=gather_task)

    # process output
    param = []
    for device_name, result in output.items():

        if result.failed:
            print(f'\n{device_name} failed:')
            for r in result:
                if r.failed:
                    print(f'{r.name} failed with {r.exception}')

        elif not isinstance(result[1].result, QDict):
                if '% BGP not active' in result[1].result:
                    print(f'\n{device_name} - BGP not active')
                else:
                    print(f'\n{device_name} - Something else went wrong - {result[1].result}')

        else:    
            for neighbor in Dq(result[1].result).get_values('neighbor'):
                param.append({ 'device_name': device_name,
                               'neighbor': neighbor,
                               'state_pfxrcd': Dq(result[1].result).contains(neighbor).get_values('state_pfxrcd')[0]
                               })

    metafunc.parametrize('data',
                          param,
                          ids=helper_id
                          )


#per bgp neighbor tests
def test_bgp_summary(data):

    state_pfxrcd = data['state_pfxrcd']

    if state_pfxrcd in ['Idle','Active']:
        pytest.fail(f'Inactive neighbor.')

    elif state_pfxrcd == 'Idle (Admin)':
        pytest.fail(f'Neighbor administratively shutdown.')

    elif state_pfxrcd == 'Idle (PfxCt)':
        pytest.fail(f'Neighbor exceed prefix limit.')

    elif not state_pfxrcd.isdigit():
        pytest.fail(f'Neighor state is: {state_pfxrcd}.')

    elif state_pfxrcd == '0':
        pytest.fail(f'Neighbor up, but no prefixes received.')
        
    # Hopefully this proves that BGP up and prefixes being received!
    return True
