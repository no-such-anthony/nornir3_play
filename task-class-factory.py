from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command


#how about a class function factory or is it factory function...?

def Task_Factory(task, *args, **kwargs):

    cmd = kwargs.get('cmd', None)
    cmdlet = kwargs.get('cmdlet', None)

    if task.host.name == 'host3':
        pass

    elif task.host.platform == 'ios' and cmd == 'show':

        if cmdlet == 'run':
            return Ios_Show_Run(*args, **kwargs)
        
    return Not_Implemented(*args, **kwargs)


class Base_Factory():

    def __init__(self, *args, **kwargs):
        self.__name__ = self.__class__.__name__


class Not_Implemented(Base_Factory):

    def __call__(self, task, *args, **kwargs):
        return f'Not implemented - {task.host.platform} - {task.host.name}' 


class Ios_Show_Run(Base_Factory):

    def __call__(self, task, *args, **kwargs):
        cmd = 'show running-config'
        result = task.run(task=netmiko_send_command, name=cmd, command_string=cmd)


    
def do_task(task):

    the_task = Task_Factory(task, cmd='show', cmdlet='run')
    task.run(the_task)


def main():

    nr = InitNornir(config_file='config.yaml')

    results = nr.run(task=do_task)
    print_result(results)


if __name__ == '__main__':
    main()
