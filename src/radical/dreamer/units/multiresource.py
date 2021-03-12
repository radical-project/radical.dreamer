
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
        if not resources or not isinstance(resources, list):
            raise Exception('List of [sub]resources is not set')
        kwargs['resources'] = resources

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('multiresource')

        core_uids = set()
        for idx in range(len(self.resources)):
            self.resources[idx] = Resource(**self.resources[idx])

            if not core_uids.isdisjoint(self.resources[idx].cores):
                raise Exception('Core(s) belongs to different Resources')
            core_uids.update(self.resources[idx].cores)

            self.cores.update(self.resources[idx].cores)

    def set_dynamic_performance(self, core_uid):
        """
        Re-generate dynamic core performance (if resource is dynamic).

        @param core_uid: Core uid.
        @type core_uid: str
        """
        for resource in self.resources:
            resource.set_dynamic_performance(core_uid=core_uid)
