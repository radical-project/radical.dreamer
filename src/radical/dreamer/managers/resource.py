
from ..units import MultiResource, Resource, Task

from ._base import Manager, ManagerRunMixin
from .ext import Schedule


class ResourceManager(Manager, ManagerRunMixin):

    _NAME = Manager.NAMES.Resource

    def __init__(self, cfg=None, cfg_path=None):
        Manager.__init__(self, cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._resource = None

    def _cfg_setup(self, cfg):
        self._schedule = Schedule(cfg=cfg.schedule)

    def _run(self):
        workload_uid = None

        while True:

            resource = self._rmq.get(self._rmq_queues.resource)
            if resource:
                if resource['uid'].startswith('multiresource'):
                    self._resource = MultiResource(**resource)
                else:
                    self._resource = Resource(**resource)
                self._logger.info('Resource (%s) received' % self._resource.uid)

            session = self._rmq.get(self._rmq_queues.session)
            if session:
                workload_uid = session.get('workload_uid')
                self._logger.info('Workload (%s) published' % workload_uid)

            if self._resource and workload_uid:

                _data = None
                while not _data:
                    # get an allocation request from request-queue
                    _data = self._rmq.get(self._rmq_queues.request)
                num_cores = _data.get('num_cores')

                # publish allocated cores (uids) to allocation-queue
                self._rmq.publish(
                    queue=self._rmq_queues.allocation,
                    data=self._schedule.get_cores_filtered(
                        resource=self._resource,
                        num_cores=num_cores,
                        uid_only=True))
                self._logger.info('List of allocated cores published')

                schedule_layout = None
                while not schedule_layout:
                    # get scheduled tasks with cores from schedule-queue
                    schedule_layout = self._rmq.get(self._rmq_queues.schedule)
                self._schedule.layout = schedule_layout
                self._logger.info('Preliminary schedule received')

                for bound_tasks in self._schedule:
                    tasks = [Task(**task) for task in bound_tasks]

                    # run tasks execution on assigned cores
                    self._resource.process(tasks)

                    # publish profile data back to session [manager]
                    self._rmq.publish(
                        queue=self._rmq_queues.profile,
                        data=Task.demunch(tasks))

                    # TODO: for strategies based on cores availability
                    #   `for cores in self._resource.released_cores:...`

                    # re-binding of tasks to cores
                    self._schedule.adaptive_binding(resource=self._resource,
                                                    num_cores=num_cores)

                workload_uid = None
                self._logger.info('Scheduled tasks executed')
