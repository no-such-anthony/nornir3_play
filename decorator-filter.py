from nornir import InitNornir
import time
from functools import wraps
import re


def _findvalue(obj, key):

    keys = key.split('.', 1)

    if len(keys) == 1:
        return obj.get(key,None)

    for k, v in obj.items():
        if isinstance(v,dict):
            item = _findvalue(v, keys[1])
            if item is not None:
                return item


def regF_and(host, filt):

    for filter_what, filter_for in filt.items():

        data = _findvalue(host,filter_what)

        if not data:
            return False

        regex_search = re.compile("^"+filter_for+"$").search

        #using str() to help with data integers, floats, and group names
        if isinstance(data, list):
            found = any (regex_search(str(data_item)) for data_item in data)
        else:
            found = bool (regex_search(str(data)))

        if not found:
            break

    return found


def nfilt(filt):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if regF_and(args[0].host, filt):
                retval = f(*args, **kwargs)
            else:
                retval = "filtered"
            return retval
        return wrap
    return decorator


@nfilt( { 'name': 'host[12]',
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
