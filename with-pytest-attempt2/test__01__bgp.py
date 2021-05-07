import pytest
from genie.utils import Dq


def bgp_active_test(item):

    if isinstance(item,dict):
        return f"{item['device_name']} bgp active"


def bgp_neighbor_test(item):

    if isinstance(item,dict):
        return f"{item['device_name']} bgp neighbor {item['neighbor']}"


@pytest.mark.parametrize('device',pytest.ptnr.get_bgp_devices(),ids=bgp_active_test)
def test_bgp_active(device):

    if not device['state']:
        pytest.fail('BGP not active.')

    return True


#per bgp neighbor tests
@pytest.mark.parametrize('neighbor',pytest.ptnr.get_bgp_neighbors(),ids=bgp_neighbor_test)
def test_bgp_summary(neighbor):
    
    host = pytest.ptnr.nr.inventory.hosts[neighbor['device_name']]
    bgp_ipv4_unicast_summary = host.data['show_bgp_ipv4_unicast_summary']
    state_pfxrcd = Dq(bgp_ipv4_unicast_summary).contains(neighbor['neighbor']).get_values('state_pfxrcd')[0]

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
        
    # Hopefull this proved that BGP up and prefixes being received!
    return True
    
