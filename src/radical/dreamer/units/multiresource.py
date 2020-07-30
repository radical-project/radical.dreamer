
from radical.utils import generate_id, Munch

from .resource import Resource, ResourceCoresMixin


class MultiResource(ResourceCoresMixin, Munch):

    _schema = {
        'uid': str,
        'resources': list,
        'cores': dict
    }

    _defaults = {
        'uid': '',
        'cores': {}
    }

    def __init__(self, resources, **kwargs):
        Munch.__init__(self, from_dict=self._defaults)

        if not resources:
            raise Exception('[Sub]resources are not set')

        if 'is_dynamic' in kwargs:
            for idx in range(len(resources)):
                resources[idx]['is_dynamic'] = kwargs['is_dynamic']
            del kwargs['is_dynamic']

        kwargs['resources'] = resources
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

    def dynamic_consistency_adjustment(self):
        """
        Re-generate cores performance for any dynamic resource.
        """
        for resource in self.resources:
            resource.dynamic_consistency_adjustment()
