
from ..units import Workload

from ._base import Manager


class WorkloadManager(Manager):

    _NAME = Manager.NAMES.Workload

    def __init__(self, cfg=None, cfg_path=None):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._workload = None

    def _get_schedule(self, cores):
        options = {'group_size': len(cores),
                   'prior_sort': True if self._cfg.early_binding else False}

        if ('largest_to_fastest' in self._cfg.schedule_options or
                'largest_to_slowest' in self._cfg.schedule_options):
            options['order_reverse'] = True

        elif ('smallest_to_fastest' in self._cfg.schedule_options or
                'smallest_to_slowest' in self._cfg.schedule_options):
            options['order_reverse'] = False

        groups = self._workload.get_task_groups(**options)
        for g_idx in range(len(groups)):
            for idx in range(len(groups[g_idx])):
                groups[g_idx][idx] = {'task': groups[g_idx][idx].as_dict(),
                                      'core': cores[idx]}
        return groups

    def run(self):
        try:
            with self._rmq:
                while True:
                    if self._workload is None:

                        workload = self._rmq.get(self._rmq_queues.workload)
                        if not workload:
                            continue

                        self._workload = Workload(**workload)
                        self._logger.info('Workload %s is received' %
                                          self._workload.uid)

                        if self._cfg.early_binding:
                            # publish an allocation request to request-queue
                            self._rmq.publish(
                                queue=self._rmq_queues.request,
                                data={'num_cores': self._workload.num_tasks})

                        cores = None
                        while not cores:
                            # get allocated "cores" from allocation-queue
                            #   NOTE: the content of each "core" element is not
                            #   important for now, more important is to have it
                            #   unique, thus current list of "cores" is actually
                            #   a list of cores' UIDs
                            cores = self._rmq.get(self._rmq_queues.allocation)
                        self._logger.info('Received allocation (uids)')

                        # publish "schedule" to schedule-queue
                        self._rmq.publish(queue=self._rmq_queues.schedule,
                                          data=self._get_schedule(cores))
                        self._logger.info('Schedule is published')

                        self._workload = None
                        self._logger.info('Workload is reset')

        except KeyboardInterrupt:
            self._logger.info('Closing %s' % self._uid)

        except Exception as e:
            self._logger.exception('WorkloadManager failed: %s' % e)

        finally:
            with self._rmq:
                self._rmq.delete()
