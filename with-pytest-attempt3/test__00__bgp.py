import pytest
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.tasks.data import load_yaml
from genie.utils import Dq
#from genie.conf.base.utils import QDict
from nornir.core.exceptions import NornirSubTaskError
import ipaddress
from netmiko import NetMikoTimeoutException, NetMikoAuthenticationException


def gathering_job(task):

    expected = task.run(task=load_yaml, file=f"./expected/{task.host}/bgp_neighbors.yaml")

    current = task.run(task=netmiko_send_command,
                       command_string='show bgp ipv4 unicast summary',
                       use_genie=True)

    expected_data = expected.result

    current_data = {}
    for neighbor in Dq(current.result).get_values('neighbor'):
        current_data[neighbor] = {}
        current_data[neighbor]['remote_as'] = Dq(current.result).contains(neighbor).get_values('as')[0]
        current_data[neighbor]['state_pfxrcd'] = Dq(current.result).contains(neighbor).get_values('state_pfxrcd')[0]

    all_neighbors = sorted(set(current_data.keys()).union(set(expected_data.keys())), key = ipaddress.IPv4Address)

    #begin merge and parameterization
    host = task.host.name
    merged_data = []

    for neighbor in all_neighbors:

        temp = {}
        temp['host'] = host
        temp['neighbor'] = neighbor
        if neighbor in current_data:
            temp['current'] = current_data[neighbor]
        if neighbor in expected_data:
            temp['expected'] = expected_data[neighbor]
        merged_data.append(temp)

    return merged_data


def pytest_generate_tests(metafunc):

    # if nornir task failed in a previous test, lets reset
    pytest.nr.data.reset_failed_hosts() 

    # gathering job
    output = pytest.nr.run(task=gathering_job)
    
    #finish merge and parameterization
    data = []
    for host, result in sorted(output.items()):

        if result.failed:
            for r in result:
                if r.failed:
                    if isinstance(r.exception, NornirSubTaskError):
                        pass
                    elif isinstance(r.exception, FileNotFoundError):
                        print(f'\n{host} - did not find expected result yaml file')
                    elif isinstance(r.exception, NetMikoTimeoutException):
                        print(f'\n{host} - TCP connection to device failed')
                    elif isinstance(r.exception, NetMikoAuthenticationException):
                        print(f'\n{host} - Authentication failed')
                    else:
                        print(f'\n{host} - {r.name} failed with {r.result}')
        else:    
            data.extend(result.result)


    metafunc.parametrize('data',
                          data,
                          ids=helper_id
                          )


def helper_id(item):

    if isinstance(item, dict):
        return f"{item['host']} bgp neighbor {item['neighbor']}"


#per bgp neighbor tests
def test_bgp_summary(data):

    if 'current' not in data and 'expected' in data:
        pytest.fail('Missing expected neighbor.')

    current = data['current']

    if 'expected' not in data and 'current' in data:
        pytest.fail('Unexpected neighbor.')

    expected = data['expected']

    if expected['remote_as'] != current['remote_as']:
        pytest.fail('Remote AS not expected.')

    elif expected['state'] == 'shutdown' and current['state_pfxrd'] != 'Idle (Admin)':
        pytest.fail('Neighbor expected to be shutdown.')

    elif expected['state'] == 'inactive' and current['state_pfxrd'] not in ['Idle','Active']:
        pytest.fail('Neighbor expected to be inactive.')

    if not current['state_pfxrcd'].isdigit():
        pytest.fail(f'Neighor state is: {state_pfxrcd}.')

    #set default prefix_test if none found
    if not expected['prefix_test']:
        expected['prefix_test'] = 'gt,0'

    o, v = expected['prefix_test'].split(',',1)
    t = int(current['state_pfxrcd'])
    v = int(v)
    
    if o == 'gt':
        if t > v:
            return True
        else:
            pytest.fail(f"Prefixes {t} is not greater than expected {v}")

    if o == 'gte':
        if t >= v:
            return True
        else:
            pytest.fail(f"Prefixes {t} is not greater than or equal to expected {v}")

    if o == 'lt':
        if t < v:
            return True
        else:
            pytest.fail(f"Prefixes {t} is not less than expected {v}")

    if o == 'lte':
        if t <= v:
            return True
        else:
            pytest.fail(f"Prefixes {t} is not less than or equal to expected {v}")

    if o == 'eq':
        if t == v:
            return True
        else:
            pytest.fail(f"Prefixes {t} does not equal expected {v}")

    if o == 'neq':
        if t != v:
            return True
        else:
            pytest.fail(f"Prefixes {t} should not equal expected {v}")

    pytest.fail('Something wrong in prefix_test syntax?')
