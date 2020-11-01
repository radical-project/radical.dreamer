
from radical.utils import generate_id, Munch

from .core import Core
from .ext import SampleDistribution


class ResourceCoresMixin:

    @property
    def num_cores(self):
        return len(self.cores)

    def process(self, tasks):
        for task in tasks:
            if task.core_uid and task.core_uid in self.cores:
                # TODO: is warning or exception needed in case of not bound task
                self.cores[task.core_uid].run(task)

    def release_cores(self, cores=None):
        cores = cores or self.cores.values()
        for core in sorted(cores, key=lambda c: (c.release_time, c.uid)):
            yield core


class Resource(Munch, ResourceCoresMixin):

    _schema = {
        'uid': str,
        'io_rate': float,
        'is_dynamic': bool,
        'cores': dict,
        'perf_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'io_rate': 0.,
        'is_dynamic': False,
        'cores': {}
    }

    def __init__(self, **kwargs):
        if 'num_cores' in kwargs:
            kwargs.setdefault('perf_dist', {})['size'] = kwargs['num_cores']
            del kwargs['num_cores']

        Munch.__init__(self, from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('resource')

        if not self.cores:
            for p in self.perf_dist.samples:
                core = Core(perf=abs(p), io_rate=self.io_rate)
                self.cores[core.uid] = core
        else:
            for uid in self.cores:
                self.cores[uid] = Core(**self.cores[uid])

    def dynamic_consistency_adjustment(self):
        """
        If resource is dynamic, then re-generate cores performance.
        """
        if self.is_dynamic:
            perf_values = self.perf_dist.samples
            for idx, core in enumerate(self.cores.values()):
                core.perf = abs(perf_values[idx])
