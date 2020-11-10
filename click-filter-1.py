#!/usr/bin/env python
from nornir import InitNornir
from nornir.core.filter import F
import click


#
#Using F filter __any, single search key, multiple search values
#no regex
#no integer or float search but you can put the value in quotes within inventory files
#
#examples
#python <script> name host1 host4
#python <script> hostname host1 host4
#python <script> groups wilma barn
#python <script> <data_variable> fred wilma
#python <script> <data_variable>__<data_variable> fred wilma barney
#


@click.command()
@click.argument('filt',nargs=-1)
def main(filt):

    nr = InitNornir(config_file='config.yaml')
    
    if len(filt) > 1:
        filter_what, filter_for = filt[0], filt[1:]
        f = F (**{ f'{filter_what}__any' : filter_for })
        nr = nr.filter(f)

    print(nr.inventory.hosts)


if __name__ == '__main__':
    main()
