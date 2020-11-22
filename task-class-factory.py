from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command


#how about a class function factory or is it factory function...?

def Task_Factory(task, **kwargs):

    cmd = kwargs.get('cmd', None)
    cmdlet = kwargs.get('cmdlet', None)

    if task.host.name == 'host3':
        pass

    elif task.host.platform == 'ios' and cmd == 'show':

        if cmdlet == 'run':
            return Ios_Show_Run(**kwargs)
        
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
