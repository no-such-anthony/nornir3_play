import pytest
from nornir import InitNornir
from nornir.core.filter import F


# Basic 'and' F filtering with --filt
#
# --filt name:host4 --filt <data_key>:home
# --filt hostname:192.168.0.1
# --filt groups__contains:wilma --filt site:barney
# --filt <data_key1>:wilma --filt <data_key2>:10
# --filt <data_key>__<nested_data_key>:fred
# --filt "tag__any:wilma, fred"
# --filt tag__any:wilma,fred
# --filt name__any:host1,host2

def pytest_addoption(parser):

    parser.addoption("--filt",
                     action="append",
                     help="Basic Nornir 'and' F filter, key:data")


def pytest_sessionstart(session):

    config = session.config
    filt = config.getoption("--filt")

    pytest.nr = InitNornir(config_file="config.yaml")

    if filt:
            fd = {}
            for a in filt:
                k, v = a.split(':')
                if k.endswith('__any'):
                    v = [x.strip() for x in v.split(',')]
                fd[k] = v
            ff = F(**fd)

            pytest.nr = pytest.nr.filter(ff)

    if len(pytest.nr.inventory.hosts.keys()) == 0:
        pytest.exit("Nothing found in Nornir inventory.")


def pytest_sessionfinish(session):

    pytest.nr.close_connections

