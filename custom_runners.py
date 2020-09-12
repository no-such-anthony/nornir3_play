from concurrent.futures import ThreadPoolExecutor, as_completed
from nornir.core.task import AggregatedResult, Task
from nornir.core.inventory import Host
from typing import List
from tqdm import tqdm

# custom runner using as_completed with tqdm
class runner_as_completed_tqdm:
    """
    ThreadedRunner runs the task over each host using threads
    Arguments:
        num_workers: number of threads to use
    """

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        """
        This is where the magic happens
        """
        # we instantiate the aggregated result
        result = AggregatedResult(task.name)

        with tqdm(total=len(hosts), desc="progress",) as progress:
            with ThreadPoolExecutor(max_workers=self.num_workers) as pool:
                futures = {pool.submit(task.copy().start, host): host for host in hosts}
                for future in as_completed(futures):
                    worker_result = future.result()
                    result[worker_result.host.name] = worker_result
                    progress.update()
                    if worker_result.failed:
                        tqdm.write(f"{worker_result.host.name}: failure")
                    else:
                        tqdm.write(f"{worker_result.host.name}: success")

        return result

# custom runner using as_completed 
class runner_as_completed:
    """
    ThreadedRunner runs the task over each host using threads
    Arguments:
        num_workers: number of threads to use
    """

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        """
        This is where the magic happens
        """
        # we instantiate the aggregated result
        result = AggregatedResult(task.name)
        with ThreadPoolExecutor(max_workers=self.num_workers) as pool:
            futures = {pool.submit(task.copy().start, host): host for host in hosts}
            for future in as_completed(futures):
                worker_result = future.result() 
                result[worker_result.host.name] = worker_result
                if worker_result.failed:
                    print(f'{worker_result.host.name} - fail')
                else:
                    print(f'{worker_result.host.name} - success')

        return result




