from nornir import InitNornir
import time
from functools import wraps
from tqdm import tqdm

# Using a decorator to generate a basic progress bar?  Crazy stuff.
# Now with 'in grouped task' progress bar using the same class!

class PBar:
    def __init__(self):
        self.enabled = True
    
    def start(self, num_hosts,pbar_title,pos):
        if self.enabled:
            self.progress = tqdm(total=num_hosts, desc=f"{pbar_title} progress",position=pos)
    
    def __call__(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            retval = f(*args, **kwargs)
            self.update()
            return retval
        return wrap

    def update(self):
        if self.enabled:
            #tqdm.write(args[0].host.name)
            self.progress.update()       

    def finish(self):
        if self.enabled:
            self.progress.close()

outer_pbar = PBar()


@outer_pbar
def master(task):

    inner_pbar = PBar()
    inner_pbar.start(2, f'{task.host} grouped tasks', 0)

    task.run(sub1)
    inner_pbar.update()

    task.run(sub2)
    inner_pbar.update()

    inner_pbar.finish()


def sub1(task):
    time.sleep(2)


def sub2(task):
    time.sleep(2)


def main():
    nr = InitNornir(config_file='dec-config.yaml')

    outer_pbar.start(len(nr.inventory.hosts), 'outer', 1)
    agg_result = nr.run(task=master)   
    outer_pbar.finish()

    print(agg_result)



if __name__ == '__main__':
    main()
