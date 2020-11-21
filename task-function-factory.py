from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command


#how about a function factory?


def task_factory(task, *args, **kwargs):

    cmd = kwargs.get('cmd', None)
    cmdlet = kwargs.get('cmdlet', None)

    def not_implemented(task, *args, **kwargs):
        return(f'{task.name} - {task.host.name}: not implemented')


    def ios_show(task, *args, **kwargs):

        def ios_show_run(task, *args, **kwargs):
            cmd = 'show running-config'
            result = task.run(task=netmiko_send_command, name=cmd, command_string=cmd)


        if cmdlet == 'run':
            return ios_show_run
        
        else:      
            return not_implemented


    if task.host.name == 'host3':
        return not_implemented

    elif task.host.platform == 'ios' and cmd == 'show':
        return ios_show(task)

    else:
        return not_implemented


def do_task(task):

    the_task = task_factory(task, cmd='show', cmdlet='run')
    task.run(the_task)


def main():

    nr = InitNornir(config_file='config.yaml')

    results = nr.run(task=do_task)
    print_result(results)


if __name__ == '__main__':
    main()
