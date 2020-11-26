from nornir import InitNornir
from nornir.core.filter import F
from nornir.core import Task
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command
from functools import wraps
import click


def build_F(filt):
    fd = {}
    for a in filt:
        k, v = a.split(':')
        fd[k] = v
    ff = F(**fd)
    #print('building filter...')

    return ff

def build_tasks(task):
    tl = []
    for a in task:
        cmds = a.split(':',1)
        td={}
        td['cmd']=cmds[0]
        if len(cmds)==2:
            td['cmdlet']=cmds[1] 
        else:
             td['cmdlet']=None
        tl.append(td)
    #print('building tasks...')

    return tl


class nfilt(object):

    def __init__(self, *args):
        if args:
            self.ff = build_F(args[0])
        else:
            self.ff = None


    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            #override global nfilt_filter if decorator has filter array argument
            if self.ff:
                ff = self.ff
            else:
                global nfilt_filter
                ff = nfilt_filter
            
            #quick and dirty check to work outside and inside of classes
            if isinstance(args[0],Task):
                arg = args[0]
            else:
                arg = args[1]

            if ff(arg.host):
                retval = f(*args, **kwargs)
            else:
                retval = "filtered"    
            return retval
        return wrapped_f


def Task_Factory(task, **kwargs):

    cmd = kwargs.get('cmd', None)
    cmdlet = kwargs.get('cmdlet', None)

    if task.host.name == 'host3':
        pass

    elif task.host.platform == 'ios' and cmd == 'show':

        if cmdlet == 'run':
            return Ios_Show_Run(**kwargs)

    elif cmd == 'sayhello':
        return Sayhello(**kwargs)
        
    return Base_Factory(**kwargs)


class Base_Factory():

    def __init__(self,**kwargs):
        self.__name__ = self.__class__.__name__
        self.init_kwargs = kwargs

    def __call__(self, task, **kwargs):
        cmd = self.init_kwargs.get('cmd', None)
        cmdlet = self.init_kwargs.get('cmdlet', None)
        return f'cmd={cmd} cmdlet={cmdlet} is not implemented for {task.host.platform} : {task.host.name}' 


class Ios_Show_Run(Base_Factory):

    def __call__(self, task, **kwargs):
        self.call_kwargs = kwargs
        #print(self.init_kwargs)
        #print(self.call_kwargs)
        cmd = 'show running-config'
        #result = task.run(task=netmiko_send_command, name=cmd, command_string=cmd)
        return cmd


class Sayhello(Base_Factory):

    @nfilt(['name:host2'])
    def __call__(self, task, **kwargs):
        self.call_kwargs = kwargs
        #print(self.init_kwargs)
        #print(self.call_kwargs)
        cmd = 'Hello, world!'
        #result = task.run(task=netmiko_send_command, name=cmd, command_string=cmd)
        return cmd


#can override CLI filter by supplying filter array as argument
#@nfilt(['name:host1'])
#@nfilt(['groups__contains:wilma','tag:fred'])
@nfilt()
def do_task(task,todo):
    for t in todo:
        the_task = Task_Factory(task, cmd=t['cmd'], cmdlet=t['cmdlet'])
        task.run(the_task)


#-f k1:v1 -f k2:v2 -t cmd -t cmd:cmdlet
@click.command()
@click.option('--filt', '-f', multiple=True)
@click.option('--task', '-t', multiple=True)
def main(filt, task):

    global nfilt_filter
    nfilt_filter = build_F(filt)

    todo = build_tasks(task)
    #print(todo)

    #override cli argument in code?
    #
    #override filers
    #filt = ['groups__contains:wilma','tag:fred']
    #nfilt_filter = build_F(filt)
    #
    #override tasks
    #task = ['show:run','sayhello']
    #todo = build_tasks(task)

    nr = InitNornir(config_file='dec-config.yaml')

    #or skip the decorator altogether and just use nr.filter with cli arguments
    #nr = nr.filter(nfilt_filter)

    result = nr.run(task=do_task,todo=todo,name="Tasks")
    print_result(result)


if __name__ == '__main__':
    main()
