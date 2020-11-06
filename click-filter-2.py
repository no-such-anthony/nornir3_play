#!/usr/bin/env python
from nornir import InitNornir
from nornir.core.filter import F
import click


#
#Using F filter and multiple search keys with single search value each
#-f k1:v1 -f k2:v2
#the filter parameters are ANDed together
#exact match
#no regex
#no integer or float search but you can put the value in quotes within inventory files
#
#examples
#python <script> -f name:host4 -f <data_variable>:home
#python <script> -f hostname:192.168.0.1
#python <script> -f groups__contains:wilma -f site:barney
#python <script> -f <data_variable1>:wilma -f <data_variable2>:10
#python <script> -f <data_variable>__<data_variable>:fred
#
#if you have a list in your data keys then you need to use __contains like in the groups filter above
#


@click.command()
@click.option('--filt', '-f', multiple=True)
def main(filt):

    nr = InitNornir(config_file='config.yaml')

    filter = {}
    for a in filt:
        k, v = a.split(':')
        filter[k] = v
    f = F(**filter)

    nr = nr.filter(f)
    print(nr.inventory.hosts)
    


if __name__ == '__main__':
    main()
