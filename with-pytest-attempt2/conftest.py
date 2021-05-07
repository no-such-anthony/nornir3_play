import pytest
from ptnr import PTNR

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
    pytest.ptnr = PTNR(filt)

    if len(pytest.ptnr.nr.inventory.hosts.keys()) == 0:
        pytest.exit("Nothing found in Nornir inventory.")


def pytest_sessionfinish(session):

    pytest.ptnr.nr.close_connections

