
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

    def __init__(self, resources, set_cores=False, **kwargs):
        if not resources or not isinstance(resources, list):
            raise Exception('List of [sub]resources is not set')
        kwargs.update({'resources': resources, 'cores': {}})

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('multiresource')

        for idx in range(len(self.resources)):

            if set_cores and not self.resources[idx].get('set_cores'):
                self.resources[idx]['set_cores'] = set_cores

            self.resources[idx] = Resource(**self.resources[idx])
            self._merge_cores(cores=self.resources[idx].cores)

    def _merge_cores(self, cores):
        if cores:
            if not set(self.cores).isdisjoint(cores):
                raise Exception('Core(s) belongs to different Resources')
            self.cores.update(cores)

    @property
    def size(self):
        return sum([r.perf_dist.size for r in self.resources])

    def set_cores(self, cores_list=None):
        """
        Re-generate Core objects.

        NOTE: this method should be used instead of direct calls per resource

        @param cores_list: List of cores descriptions.
        @type cores_list: list/None
        """
        self.cores.clear()

        max_size = len(self.resources)
        cores_list = [] if not cores_list else list(cores_list)[:max_size]
        # cores: [{..}, {..}, {..},.., None]
        cores_list.extend([None] * (max_size - min(len(cores_list), max_size)))

        for idx in range(max_size):
            self.resources[idx].set_cores(cores=cores_list[idx])
            self._merge_cores(cores=self.resources[idx].cores)

    def set_dynamic_performance(self, core_uid):
        """
        Re-generate dynamic core performance (if resource is dynamic).

        @param core_uid: Core uid.
        @type core_uid: str
        """
        for resource in self.resources:
            resource.set_dynamic_performance(core_uid=core_uid)
