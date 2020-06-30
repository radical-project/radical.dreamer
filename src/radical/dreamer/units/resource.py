
from radical.utils import generate_id, Munch

from .core import Core
from .ext import SampleDistribution


class Resource(Munch):

    _schema = {
        'uid': str,
        'io_rate': float,
        'cores': list,
        'perf_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'io_rate': 0.,
        'cores': []
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=self._defaults)

        if 'num_cores' in kwargs:
            kwargs.setdefault('perf_dist', {})['size'] = kwargs['num_cores']
            del kwargs['num_cores']

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('resource')

        if not self.cores:
            self.cores = [Core(perf=abs(p), io_rate=self.io_rate)
                          for p in self.perf_dist.generate()]
        else:
            for idx in range(self.num_cores):
                self.cores[idx] = Core(**self.cores[idx])

    @property
    def num_cores(self):
        return len(self.cores)

    def as_dict(self):
        output = super().as_dict()
        output['cores'] = [c.as_dict() for c in self.cores]
        return output

    def get_cores(self, *args):
        """
        Get all [or subset] of cores that are of a certain order (if no
        conditions are set then all cores of a random order will be returned).

        :arg value "fastest_first" - core with higher Perf goes first
        :arg value "slowest_first" - core with lower Perf goes first
        """
        if 'fastest_first' in args:
            output = sorted(self.cores, key=lambda c: c.perf, reverse=True)
        elif 'slowest_first' in args:
            output = sorted(self.cores, key=lambda c: c.perf)
        else:
            from random import shuffle
            output = list(self.cores)
            shuffle(output)
        return output

    def generate_cores_perf(self):
        """
        Re-generate new Perf values for all cores.
        """
        perf_values = self.perf_dist.generate()
        for idx, core in enumerate(self.cores):
            core.perf = abs(perf_values[idx])
