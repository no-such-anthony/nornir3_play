#!/usr/bin/env python
from nornir import InitNornir
from nornir.core.filter import F
import click


#examples
#python <script> host host1 host4
#python <script> hostname host1 host4
#python <script> groups wilma barney
#python <script> <data_variable> fred wilma
@click.command()
@click.argument('filt',nargs=-1)
def main(filt):
    nr = InitNornir(config_file='config.yaml')

    if len(filt) > 1:
        filter_what, filter_for = filt[0], filt[1:]
        if filter_what == 'host':
            nr = nr.filter(filter_func=lambda h: h.name in filter_for)
        else:
            #only does __any but could introduce click option for __all
            nr = eval(f'nr.filter(F({filter_what}__any=filter_for))') 

    print(nr.inventory.hosts)    


if __name__ == '__main__':
    main()


