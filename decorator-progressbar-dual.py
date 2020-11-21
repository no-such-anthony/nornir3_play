from nornir import InitNornir
import time
from functools import wraps
from tqdm import tqdm
import sys

# Using a decorator to generate a basic progress bar?  Crazy stuff.
# Now with 'in grouped task' progress bar using the same class.

class PBar:

    _shared_state = {}

    def __init__(self):
        self.enabled = True
        
        if self._shared_state.get('first', True):
            self._shared_state['first'] = False
            self.pos = 0
            self.colour = 'green'
        else:
            self.pos = None
            self.colour = 'blue'

    
    def start(self, num_hosts,pbar_title):
        if self.enabled:
            self.progress = tqdm(total=num_hosts, desc=f"{pbar_title} progress",
                                position=self.pos,colour=self.colour,
                                leave=None
                                #file=sys.stdout
                                )
    
    def __call__(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            retval = f(*args, **kwargs)
            self.update()
            return retval
        return wrap

    def update(self):
        if self.enabled:
            self.progress.update()
            self.progress.refresh()

    def finish(self):
        if self.enabled:
            self.progress.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        #Exception handling here
        self.finish()

outer_pbar = PBar()


@outer_pbar
def master(task):

    the_jobs = ['job1','job2','job3']
    with PBar() as inner_pbar:
        inner_pbar.start(len(the_jobs), f'{task.host} tasks')
        for cmd in the_jobs:
            task.run(sub1,name=cmd,cmd=cmd)
            inner_pbar.update()


def sub1(task,cmd):
    time.sleep(2)



def main():
    nr = InitNornir(config_file='dec-config.yaml')

    outer_pbar.start(len(nr.inventory.hosts), 'outer')
    agg_result = nr.run(task=master)   
    outer_pbar.finish()

    print(agg_result)



if __name__ == '__main__':
    main()
