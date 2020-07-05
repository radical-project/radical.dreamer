
import random

from radical.utils import generate_id, Munch

from .resource import Resource


class MultiResource(Munch):

    _schema = {
        'uid': str,
        'resources': list,
        'cores': dict
    }

    _defaults = {
        'uid': ''
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=self._defaults)
        self.cores = {}

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('multiresource')

        for idx in range(len(self.resources)):
            self.resources[idx] = Resource(**self.resources[idx])
            self.cores.update(self.resources[idx].cores)

    @property
    def num_cores(self):
        return len(self.cores)

    def as_dict(self):
        output = super().as_dict()
        for idx in range(len(output['resources'])):
            output['resources'][idx] = output['resources'][idx].as_dict()
            for uid in output['resources'][idx]['cores']:
                output['cores'][uid] = output['resources'][idx]['cores'][uid]
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
        for resource in self.resources:
            resource.generate_cores_perf()
