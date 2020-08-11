
import random

from radical.utils import generate_id, Munch

from .core import Core
from .ext import SampleDistribution


class ResourceCoresMixin:

    @property
    def num_cores(self):
        return len(self.cores)

    @staticmethod
    def reorder_cores(cores, reverse=None):
        """
        Reorder cores according to the mode (input parameter will be changed).

        :param cores: Core objects.
        :type cores: list
        :param reverse: Sorting direction (reverse=True -> fastest_first).
        :type reverse: bool/None
        """
        if reverse is not None:
            cores.sort(key=lambda c: c.perf, reverse=reverse)

    def get_cores(self, num=None, order_reverse=None, prior_sort=False):
        """
        Get all [or subset] of cores that are of a certain order (if no
        conditions are set then all cores of a random order will be returned).

        :param num: Number of returned cores, if None then return all cores.
        :type num: int/None
        :param order_reverse: Sorting direction.
        :type order_reverse: bool/None
        :param prior_sort: Flag to pick prior sorted cores (late-binding).
        :type prior_sort: bool
        :return: Core objects.
        :rtype: list
        """
        output = list(self.cores.values())
        if ((num and num < self.num_cores and not prior_sort) or
                order_reverse is None):
            random.shuffle(output)
            output = output[:num]

        self.reorder_cores(output, order_reverse)

        if num and prior_sort and order_reverse is not None:
            output = output[:num]

        return output


class Resource(ResourceCoresMixin, Munch):

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
        'is_dynamic': False
    }

    def __init__(self, **kwargs):
        Munch.__init__(self, from_dict=self._defaults)

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

    def as_dict(self):
        output = super().as_dict()
        for uid in output['cores']:
            output['cores'][uid] = output['cores'][uid].as_dict()
        return output

    def dynamic_consistency_adjustment(self):
        """
        If resource is dynamic, then re-generate cores performance.
        """
        if self.is_dynamic:
            perf_values = self.perf_dist.samples
            for idx, core in enumerate(self.cores.values()):
                core.perf = abs(perf_values[idx])
