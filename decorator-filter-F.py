from nornir import InitNornir
from nornir.core.filter import F
import time
from functools import wraps
import re


def nfilt(filt):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            ff = F(**filt)
            if ff(args[0].host):
                retval = f(*args, **kwargs)
            else:
                retval = "filtered"
            return retval
        return wrap
    return decorator


@nfilt( { 'name': 'host1',
          'tag': 'fred'} )
def show_version(task):
    time.sleep(2)
    return('ran it')


def main():
    nr = InitNornir(config_file='dec-config.yaml')
    agg_result = nr.run(task=show_version)
    for hostname, multi_result in agg_result.items():
        print(hostname, multi_result[0].result)


if __name__ == '__main__':
    main()
