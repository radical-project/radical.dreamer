
from ..exceptions import RDTypeError
from ..units import MultiResource, Resource, Workload

from ._base import Manager


class Session(Manager):

    _NAME = Manager.NAMES.Session

    def __init__(self, cfg=None, cfg_path=None, new_resource=False):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.publish(queue=self._rmq_queues.session,
                              data={'sid': self._uid,
                                    'new_resource': new_resource})

    def set_resource(self, resource):
        """
        Get Resource and publish it to RMQ: routing_key=rabbitmq.queues.resource

        :param resource: Resource description.
        :type resource: radical.dreamer.units.(multi)resource.(Multi)Resource
        """
        if not isinstance(resource, (Resource, MultiResource)):
            raise RDTypeError(expected_type=Resource,
                              actual_type=type(resource))

        with self._rmq:
            self._rmq.publish(queue=self._rmq_queues.resource,
                              data=resource.as_dict())

    def set_workload(self, workload):
        """
        Get Workload and publish it to RMQ: routing_key=rabbitmq.queues.workload

        :param workload: Workload description.
        :type workload: radical.dreamer.units.workload.Workload
        """
        if not isinstance(workload, Workload):
            raise RDTypeError(expected_type=Workload,
                              actual_type=type(workload))

        with self._rmq:
            self._rmq.publish(queue=self._rmq_queues.workload,
                              data=workload.as_dict())
