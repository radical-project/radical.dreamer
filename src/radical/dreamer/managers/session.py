
import json

from ..exceptions import RDTypeError
from ..units import Resource, Workload

from ._base import Manager


class Session(Manager):

    _NAME = Manager.NAMES.Session

    def __init__(self, cfg=None, cfg_path=None, new_resource=False):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.publish(self._rmq_queues.session,
                              json.dumps({'sid': self._uid,
                                          'new_resource': new_resource}))

    def set_resource(self, resource):
        """
        Get Resource and publish it to RMQ: routing_key=rabbitmq.queues.resource

        :param resource: Resource description.
        :type resource: radical.dreamer.units.resource.Resource
        """
        if not isinstance(resource, Resource):
            raise RDTypeError(expected_type=Resource,
                              actual_type=type(resource))

        with self._rmq:
            self._rmq.publish(self._rmq_queues.resource,
                              json.dumps(resource.as_dict()))

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
            self._rmq.publish(self._rmq_queues.workload,
                              json.dumps(workload.as_dict()))
