#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
from nornir.core.task import AggregatedResult, Task
from nornir.core.inventory import Host
from typing import List

#simple gevent runner. nothing fancy just using threading from gevent instead of concurrent.futures.
class gevent_runner:

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:

        result = AggregatedResult(task.name)
        futures = []
        greenlets = []

        pool = Pool(self.num_workers)

        for host in hosts:
            greenlet = pool.spawn(task.copy().start, host)
            greenlets.append(greenlet)
        
        pool.join()
        futures = [greenlet.get() for greenlet in greenlets]

        for future in futures:
            worker_result = future
            result[worker_result.host.name] = worker_result

        return result
