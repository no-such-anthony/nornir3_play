#!/usr/bin/env python
from nornir import InitNornir
import click
import re


#
#uses custom filter with regex
#single search key, multiple search values
#
#examples
#python <script> name host1 host4
#python <script> name "host1|host2"
#python <script> name host[12]
#python <script> groups wil.* barn.*
#python <script> <data_variable> fred wilma
#python <script> <data_variable> 65535
#python <script> <data_variable>.<data_variable> fred wilma
#


def regF(host, filt):


    def _findvalue(obj, key):
        keys = key.split('.', 1)

        if len(keys) == 1:
            return obj.get(key,None)

        for k, v in obj.items():
            if isinstance(v,dict):
                item = _findvalue(v, keys[1])
                if item is not None:
                    return item


    filter_what, filter_for = filt[0], filt[1:]
    
    if filter_what in ['name','platform','groups','hostname','username','password','port']:
        data = host.get(filter_what, None)
    else:
        data = _findvalue(dict(host.data.items()),filter_what)

    if not data:
        return False

    found = False
    regex_searches = [re.compile("^"+pattern+"$").search for pattern in filter_for]

    #using str() to help with integers, floats, and group names
    if isinstance(data, (str, int, float)):
        found = any (regex_search(str(data)) for regex_search in regex_searches)
    elif isinstance(data, list):
        found = any (regex_search(str(data_item)) for data_item in data for regex_search in regex_searches)
    else:
        # nothing else?
        found = False

    return found


@click.command()
@click.argument('filt',nargs=-1)
def main(filt):

    nr = InitNornir(config_file='config.yaml')
    
    if len(filt) > 1:
        nr = nr.filter(filter_func=regF, filt=filt)

    print(nr.inventory.hosts)    


if __name__ == '__main__':
    main()
