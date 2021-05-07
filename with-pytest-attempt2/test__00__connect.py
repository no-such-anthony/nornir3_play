import pytest


def connection_ids(item):

    if isinstance(item,dict):
        return f"{item['device_name']} connection setup"


@pytest.mark.parametrize('connect',pytest.ptnr.get_device_conns(),ids=connection_ids)
def test_connection(connect): 

    if not connect['state']:
        pytest.fail('Could not complete connection/authentication setup.')

    return True
    



    

