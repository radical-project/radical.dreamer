
import random

from radical.utils import generate_id, Munch

from .core import Core
from .ext import SampleDistribution


class Resource(Munch):

    _schema = {
        'uid': str,
        'io_rate': float,
        'cores': dict,
        'perf_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'io_rate': 0.
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
            self.cores = {}
            for p in self.perf_dist.samples:
                core = Core(perf=abs(p), io_rate=self.io_rate)
                self.cores[core.uid] = core
        else:
            for uid in self.cores:
                self.cores[uid] = Core(**self.cores[uid])

    @property
    def num_cores(self):
        return len(self.cores)

    def as_dict(self):
        output = super().as_dict()
        for uid in output['cores']:
            output['cores'][uid] = output['cores'][uid].as_dict()
        return output

    def get_cores(self, num=None, mode=None, prior_sort=False):
        """
        Get all [or subset] of cores that are of a certain order (if no
        conditions are set then all cores of a random order will be returned).

        :param num: Number of returned cores, if None then return all cores.
        :type num: int/None
        :param mode: Mode of sorting (fastest_first, slowest_first) or random.
        :type mode: str/None
        :param prior_sort: Flag to pick prior sorted cores (late-binding).
        :type prior_sort: bool
        :return: Core objects.
        :rtype: list
        """
        output = list(self.cores.values())
        if (num and num < self.num_cores and not prior_sort) or mode is None:
            random.shuffle(output)
            output = output[:num]

        if mode:
            if mode == 'fastest_first':
                output.sort(key=lambda c: c.perf, reverse=True)
            elif mode == 'slowest_first':
                output.sort(key=lambda c: c.perf)

            if num and prior_sort:
                output = output[:num]

        return output

    def generate_cores_perf(self):
        """
        Re-generate new Perf values for all cores.
        """
        perf_values = self.perf_dist.samples
        for idx, core in enumerate(self.cores.values()):
            core.perf = abs(perf_values[idx])
