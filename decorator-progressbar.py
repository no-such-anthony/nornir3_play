from nornir import InitNornir
import time
from functools import wraps
from tqdm import tqdm

# Using a decorator to generate a basic progress bar?  Crazy stuff!

class PBar:
    def __init__(self):
        self.enabled = True
    
    def start(self, num_hosts):
        if self.enabled:
            self.progress = tqdm(total=num_hosts, desc="progress",)
    
    def __call__(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            retval = f(*args, **kwargs)
            if self.enabled:
                tqdm.write(args[0].host.name)
                self.progress.update()
                self.progress.refresh()
            return retval
        return wrap

    def finish(self):
        if self.enabled:
            self.progress.close()

pbar = PBar()

@pbar
def show_version(task):
    time.sleep(2)


def main():
    nr = InitNornir(config_file='dec-config.yaml')
    # first run
    pbar.start(len(nr.inventory.hosts))
    agg_result = nr.run(task=show_version)
    pbar.finish()
    print(agg_result)

    # second run
    pbar.start(len(nr.inventory.hosts))
    agg_result = nr.run(task=show_version)
    pbar.finish()
    print(agg_result)

if __name__ == '__main__':
    main()
