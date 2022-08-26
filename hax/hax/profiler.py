import logging
import psutil
import os
import subprocess

from threading import Event

from hax.exception import InterruptedException
from hax.motr import log_exception
from hax.types import StoppableThread

from time import sleep

LOG = logging.getLogger('hax')


class Profiler(StoppableThread):

    """
    Hax Profiler thread that periodically logs hax's cpu and
    memory usage.
    """

    def __init__(self):
        super().__init__(target=self._execute,
                         name='hax profiler',
                         args=())
        self.stopped = False
        self.event = Event()

    def stop(self) -> None:
        LOG.debug('Stop signal received')
        self.stopped = True
        self.event.set()

    @log_exception
    def _execute(self):
        try:
            LOG.debug('Hax profiler has started')
            while not self.stopped:
                memory_actual = psutil.Process(
                    os.getpid()).memory_full_info()
                # cpu_usage = psutil.Process(
                #      os.getpid()).cpu_percent(interval=2)
                memory_virutal = psutil.virtual_memory()
                # wait_for_event(self.event, 2)
                memory_swap = psutil.swap_memory()
                list_path = [
                    "/sys/fs/cgroup/cpu/cpuacct.usage_percpu",
                    "/sys/fs/cgroup/cpu/cpuacct.usage",
                    "/sys/fs/cgroup/cpu/cpuacct.stat",
                    "/sys/fs/cgroup/cpu/cpu.stat",
                    "/sys/fs/cgroup/cpu/cpu.shares",
                    "/sys/fs/cgroup/cpu/cpu.rt_runtime_us",
                    "/sys/fs/cgroup/cpu/cpu.rt_period_us",
                    "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
                    "/sys/fs/cgroup/cpu/cpu.cfs_period_us",
                    "/sys/fs/cgroup/memory/memory.use_hierarchy",
                    "/sys/fs/cgroup/memory/memory.usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.swappiness",
                    "/sys/fs/cgroup/memory/memory.stat",
                    "/sys/fs/cgroup/memory/memory.soft_limit_in_bytes",
                    "/sys/fs/cgroup/memory/memory.oom_control",
                    "/sys/fs/cgroup/memory/memory.numa_stat",
                    "/sys/fs/cgroup/memory/memory.move_charge_at_immigrate",
                    "/sys/fs/cgroup/memory/memory.memsw.usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.memsw.max_usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes",
                    "/sys/fs/cgroup/memory/memory.memsw.failcnt",
                    "/sys/fs/cgroup/memory/memory.max_usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.limit_in_bytes",
                    "/sys/fs/cgroup/memory/memory.failcnt"
                ]
                lst = [
                    "/sys/fs/cgroup/memory/memory.memsw.usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.memsw.max_usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.max_usage_in_bytes",
                    "/sys/fs/cgroup/memory/memory.usage_in_bytes"
                ]
                LOG.info("Actual memory in bytes = {0!r}".format(
                    memory_actual))
                LOG.info("Virtual memory in bytes = {0!r}".format(
                    memory_virutal))
                LOG.info("swap memory in bytes = {0!r}".format(
                    memory_swap))
                for i in list_path:
                    if os.path.exists(i):
                        if i in lst:
                            i = i + " | numfmt --to=iec"
                        op = subprocess.check_output(f'cat {i}', shell=True)
                        LOG.info(f"cmd: cat {i!r}\nOutput: {op!r}")
                sleep(10)
        except InterruptedException:
            # No op. sleep() has interrupted before the timeout exceeded:
            # the application is shutting down.
            # There are no resources that we need to dispose specially.
            pass
        except Exception:
            LOG.exception('Aborting due to an error')
        finally:
            LOG.debug('profiler exited')
