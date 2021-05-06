import pytest
from nornir import InitNornir
from nornir.core.filter import F


class NORNIRconfig(object):
    """ for Nornir specific config / runtime """
    pass


def pytest_addoption(parser):
    parser.addoption("--name",
                     help='nornir device name')


def pytest_sessionstart(session):
    config = session.config
    
    #Unused, but originally had config._nr.nr so that there could be other
    #Nornir specific session information
    #config._nr = NORNIRconfig()

    device_name = config.getoption("--name")

    pytestnr = InitNornir(config_file="config.yaml")

    if device_name:
        pytestnr = pytestnr.filter(F(name=device_name))

    if len(pytestnr.inventory.hosts.keys()) == 0:
        pytest.exit("Nothing found in Nornir inventory.")

    config._nr = pytestnr


def pytest_sessionfinish(session):
    config = session.config
    config._nr.close_connections


@pytest.fixture(scope='session')
def nr(request):
    return request.config._nr

