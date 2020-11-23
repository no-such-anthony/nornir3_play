from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from functools import wraps
import click


def build_F(filt):
    fd = {}
    for a in filt:
        k, v = a.split(':')
        fd[k] = v
    ff = F(**fd)

    return ff


class nfilt(object):

    def __init__(self, *args):
        self.args = args

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            #override global nfilt_filter if decorator has filter array
            if self.args:
                ff = build_F(self.args[0])
            else:
                global nfilt_filter
                ff = nfilt_filter
            if ff(args[0].host):
                retval = f(*args, **kwargs)
            else:
                retval = "filtered"    
            return retval
        return wrapped_f


#can override CLI filter by supplying filter array as argument
#@nfilt(['name:host1'])
#@nfilt(['groups__contains:wilma','tag:fred'])
@nfilt()
def show_versions(task):
    msg = f'{task.host.name} - running...'
    print(msg)
    return msg


#-f k1:v1 -f k2:v2
@click.command()
@click.option('--filt', '-f', multiple=True)
def main(filt):

    global nfilt_filter
    nfilt_filter = build_F(filt)
    
    #override cli argument in code?
    #filt = ['groups__contains:wilma','tag:fred']
    #nfilt_filter = build_F(filt)

    nr = InitNornir(config_file='dec-config.yaml')

    #or skip the decorator altogether and just use nr.filter with cli arguments
    #nr = nr.filter(nfilt_filter)

    result = nr.run(task=show_versions)
    print_result(result)


if __name__ == '__main__':
    main()
