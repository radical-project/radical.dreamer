
from radical.utils import generate_id, Munch

from .core import Core
from .ext import SampleDistribution


class ResourceCoresMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._busy_cores = []

    @property
    def num_cores(self):
        return len(self.cores)

    def process(self, tasks):
        for task in tasks:
            if task.core_uid and task.core_uid in self.cores:
                self.set_dynamic_performance(task.core_uid)
                # TODO: exception in case of not bound task?
                # TODO: exception in case of core is already in a busy list?
                self.cores[task.core_uid].run(task)
                self._busy_cores.append(self.cores[task.core_uid])
        self._busy_cores.sort(key=lambda c: c.release_time)

    @property
    def planned_release_times(self):
        return {c.uid: c.planned_release_time for c in self._busy_cores}

    @property
    def released_cores(self):
        if self._busy_cores:
            cores = []
            release_time = self._busy_cores[0].release_time
            while release_time == self._busy_cores[0].release_time:
                cores.append(self._busy_cores.pop(0))
            yield cores


class Resource(ResourceCoresMixin, Munch):

    _schema = {
        'uid': str,
        'io_rate': float,
        'cores': dict,
        'perf_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'io_rate': 0.,
        'cores': {}
    }

    def __init__(self, **kwargs):
        if 'num_cores' in kwargs:
            kwargs.setdefault('perf_dist', {})['size'] = kwargs['num_cores']
            del kwargs['num_cores']

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('resource')

        if not self.cores:
            for p in self.perf_dist.samples:
                core = Core(perf=abs(p), io_rate=self.io_rate)
                self.cores[core.uid] = core
        else:
            for uid in self.cores:
                self.cores[uid] = Core(**self.cores[uid])

    def set_dynamic_performance(self, core_uid):
        """
        Re-generate dynamic core performance (if resource is dynamic).

        @param core_uid: Core uid.
        @type core_uid: str
        """
        if core_uid in self.cores:
            core = self.cores[core_uid]
            core.perf_dynamic = self.perf_dist.sample_temporal(mean=core.perf)
