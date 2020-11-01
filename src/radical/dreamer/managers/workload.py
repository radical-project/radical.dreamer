
from ..units import Workload

from ._base import Manager, ManagerRunMixin
from .ext import Schedule


class WorkloadManager(Manager, ManagerRunMixin):

    _NAME = Manager.NAMES.Workload

    def __init__(self, cfg=None, cfg_path=None):
        Manager.__init__(self, cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._workload = None

    def _cfg_setup(self, cfg):
        self._schedule = Schedule(cfg=cfg.schedule)

    def _run(self):
        while True:

            if self._workload is None:

                workload = self._rmq.get(self._rmq_queues.workload)
                if not workload:
                    continue

                self._workload = Workload(**workload)
                self._logger.info('Workload (%s) received' % self._workload.uid)

                # publish an allocation request to request-queue
                self._rmq.publish(
                    queue=self._rmq_queues.request,
                    data={'num_cores': self._workload.num_tasks})

                cores = None
                while not cores:
                    # get allocated "cores" (core uids) from allocation-queue
                    cores = self._rmq.get(self._rmq_queues.allocation)
                self._logger.info('List of allocated cores received')

                # create [early] schedule (i.e., execution plan)
                self._schedule.binding(
                    tasks_grouped=self._schedule.get_tasks_grouped(
                        workload=self._workload,
                        group_size=len(cores)),
                    core_uids=cores)

                # publish "schedule" to schedule-queue
                self._rmq.publish(queue=self._rmq_queues.schedule,
                                  data=self._schedule.layout)
                self._logger.info('Schedule layout published')

                self._workload = None
                self._logger.info('Workload reset')
