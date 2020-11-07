#!/usr/bin/env python
from nornir import InitNornir
import click
import re


#
#uses custom filter with regex
# -f k1:v1 -f k2:v2
#the filter parameters are ANDed together
#
#examples
#python <script> -f name:host4 -f site:home
#python <script> -f name:host[12] -f groups:wilma
#python <script> -f "name:host1|host2" -f groups:wilma
#python <script> -f name:"host1|host2" -f groups:wilma
#python <script> -f hostname:192.168.0.1
#python <script> -f groups:wilma -f site:barney
#python <script> -f <data_variable>:wilma
#python <script> -f <data_variable>.<data_variable>:10
#
#

def regFmulti(host, filt):


    def _findvalue(obj, key):
        keys = key.split('.', 1)

        if len(keys) == 1:
            return obj.get(key,None)

        for k, v in obj.items():
            if isinstance(v,dict):
                item = _findvalue(v, keys[1])
                if item is not None:
                    return item

    fd = {}
    for a in filt:
        k, v = a.split(':')
        fd[k] = v

    for filter_what, filter_for in fd.items():

        data = _findvalue(host,filter_what)

        if not data:
            return False

        found = False
        regex_search = re.compile("^"+filter_for+"$").search

        #using str() to help with data integers, floats, and group names
        if isinstance(data, (str, int, float)):
            found = bool (regex_search(str(data)))
        elif isinstance(data, list):
            found = any (regex_search(str(data_item)) for data_item in data)
        else:
            # nothing else?
            pass

        if not found:
            break

    return found


@click.command()
@click.option('--filt', '-f', multiple=True)
def main(filt):

    nr = InitNornir(config_file='config.yaml')

    nr = nr.filter(filter_func=regFmulti, filt=filt)
    print(nr.inventory.hosts)
    

if __name__ == '__main__':
    main()
