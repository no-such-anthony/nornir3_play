#!/usr/bin/env python
from nornir import InitNornir
from nornir.core.filter import F
import click
import re


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
    regex_searches = [re.compile("^"+pattern+"$").search for pattern in filter_for]
    if filter_what=='host':
        filter_what = 'name'

    if filter_what in ['name','platform','groups','hostname','username','password','port']:
        a = host.get(filter_what, None)
    else:
        a = _findvalue(dict(host.data.items()),filter_what)

    if not a:
        return False

    filter_what = a
    #using __str__() as a hack for integers, and as a hack for group name
    if isinstance(filter_what, str) or isinstance(filter_what, int):
        x = any (regex_search(filter_what.__str__()) for regex_search in regex_searches)
    elif isinstance(filter_what, list):
        x = any (regex_search(filter_item.__str__()) for filter_item in filter_what for regex_search in regex_searches)
    else:
        # nothing else?
        x = False

    return x


@click.command()
@click.argument('filt',nargs=-1)
def main(filt):
    nr = InitNornir(config_file='config.yaml')

    #method 1
    #custom filter with regex
    #examples
    #python <script> host host1 host4
    #python <script> name host1 host4
    #python <script> hostname host[14]
    #python <script> groups wil.* barn.*
    #python <script> <data_variable> fred wilma
    #python <script> <data_variable> 65535
    #python <script> <data_variable>.<data_variable> fred wilma

    if len(filt) > 1:
        nr = nr.filter(filter_func=regF, filt=filt)

    print(nr.inventory.hosts)    

    #method 2
    #just using __any much simpler, no custom filter, but exact match, no regex, no integer search?
    #examples
    #python <script> host host1 host4
    #python <script> name host1 host4
    #python <script> hostname host1 host4
    #python <script> groups wilma barney
    #python <script> <data_variable> fred wilma
    #python <script> <data_variable>__<data_variable> fred wilma

    if len(filt) > 1:
        filter_what, filter_for = filt[0], filt[1:]
        if filter_what == 'host':
            filter_what = 'name'
        F_magic = { f'{filter_what}__any' : filter_for }
        nr = nr.filter(F(**F_magic))

    print(nr.inventory.hosts)

    #method 3 - handles multiple input options
    #
    # -f k1:v1 -f k2:v2 
    #
    #filter = {}
    #for a in args:
    #    k, v = a.split(“:”)
    #    filter[k] = v
    #f = F(**filter)
    #
    #nr.filter(F(**kwargs))
    #


if __name__ == '__main__':
    main()

