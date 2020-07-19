
from radical.utils import generate_id, Munch

from .resource import Resource, ResourceCoresMixin


class MultiResource(ResourceCoresMixin, Munch):

    _schema = {
        'uid': str,
        'resources': list,
        'cores': dict
    }

    _defaults = {
        'uid': ''
    }

    def __init__(self, **kwargs):
        Munch.__init__(self, from_dict=self._defaults)
        self.cores = {}

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('multiresource')

        for idx in range(len(self.resources)):
            self.resources[idx] = Resource(**self.resources[idx])
            self.cores.update(self.resources[idx].cores)

    def as_dict(self):
        output = super().as_dict()
        for idx in range(len(output['resources'])):
            output['resources'][idx] = output['resources'][idx].as_dict()
            for uid in output['resources'][idx]['cores']:
                output['cores'][uid] = output['resources'][idx]['cores'][uid]
        return output

    def generate_cores_perf(self):
        """
        Re-generate new Perf values for all cores.
        """
        for resource in self.resources:
            resource.generate_cores_perf()
