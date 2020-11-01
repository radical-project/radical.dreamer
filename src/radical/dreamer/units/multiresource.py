
from radical.utils import generate_id, Munch

from .resource import Resource, ResourceCoresMixin


class MultiResource(Munch, ResourceCoresMixin):

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
        if not resources or not isinstance(resources, list):
            raise Exception('List of [sub]resources is not set')

        if 'is_dynamic' in kwargs:
            for idx in range(len(resources)):
                resources[idx]['is_dynamic'] = kwargs['is_dynamic']
            del kwargs['is_dynamic']

        kwargs['resources'] = resources

        Munch.__init__(self, from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('multiresource')

        for idx in range(len(self.resources)):
            self.resources[idx] = Resource(**self.resources[idx])
            self.cores.update(self.resources[idx].cores)

    def dynamic_consistency_adjustment(self):
        """
        Re-generate cores performance for any dynamic resource.
        """
        for resource in self.resources:
            resource.dynamic_consistency_adjustment()
