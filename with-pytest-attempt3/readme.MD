Extending attempt1 I got around to reading expected results from a yaml file and then comparing actual vs expected.

![](https://github.com/no-such-anthony/nornir3_play/blob/master/with-pytest-attempt3/example%20usage.PNG)

If you don't want to inject the nornir object into the pytest namespace as is here, you can always store within pytest session config. Something like
```
def pytest_sessionstart(session):
    config = session.config
    config.nornir_nr = InitNornir(config_file="config.yaml")
    ...

def pytest_sessionfinish(session):
    config = session.config
    config.nornir_nr.close_connections
 
...

def pytest_generate_tests(metafunc):
    config = metafunc.config
    config.nornir_nr etc
    ...
```
    
Like I experimented with here when I added Genie into the mix - https://gist.github.com/no-such-anthony/08e5dbc10d121003b7182a188ec0300e
