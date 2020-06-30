
import json

from ..units import Resource, Workload

from ._base import Manager


class WorkloadManager(Manager):

    _NAME = Manager.NAMES.Workload

    def __init__(self, cfg=None, cfg_path=None):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._resource = None
        self._workload = None

    @property
    def _schedule(self):
        if 'largest_to_fastest' in self._cfg.schedule_options:
            cores = self._resource.get_cores('fastest_first')
            tasks = self._workload.get_tasks('largest_first')

        elif 'smallest_to_fastest' in self._cfg.schedule_options:
            cores = self._resource.get_cores('fastest_first')
            tasks = self._workload.get_tasks('smallest_first')

        elif 'round_robin' in self._cfg.schedule_options:
            cores = list(self._resource.cores)
            tasks = list(self._workload.tasks)

        else:
            cores = self._resource.get_cores()
            tasks = self._workload.get_tasks()

        pairs = {}
        for idx, task in enumerate(tasks):
            pairs[task.uid] = {'core': cores[idx % len(cores)].as_dict(),
                               'task': task.as_dict()}

        output = []
        for task in self._workload.get_tasks(*self._cfg.schedule_options):
            output.append(pairs[task.uid])
        return output

    def run(self):
        try:
            with self._rmq:
                while True:

                    resource_msg = self._rmq.get(self._rmq_queues.resource)
                    if resource_msg:
                        self._resource = Resource(**json.loads(resource_msg))
                        self._logger.info('Resource %s is received' %
                                          self._resource.uid)

                    if self._resource and self._workload is None:

                        workload_msg = self._rmq.get(self._rmq_queues.workload)
                        if not workload_msg:
                            continue
                        self._workload = Workload(**json.loads(workload_msg))
                        self._logger.info('Workload %s is received' %
                                          self._workload.uid)

                        # publish "schedule" at schedule-queue
                        self._rmq.publish(self._rmq_queues.schedule,
                                          json.dumps(self._schedule))
                        self._logger.info('Schedule is published')

                        self._workload = None
                        if self._cfg.dynamic_resource:
                            self._resource.generate_cores_perf()
                        self._logger.info('Workload [and Resource] are reset')

                        cores_msg = None
                        while not cores_msg:
                            # get delivered "cores" from execute-queue
                            cores_msg = self._rmq.get(self._rmq_queues.execute)
                        self._logger.info('Received updates for cores')

                        cores = json.loads(cores_msg)
                        for core in cores:
                            for c in self._resource.cores:
                                if core['uid'] == c.uid:
                                    c.util = core['util']
                                    c.task_history = core['task_history']
                        self._logger.info('Cores are updated')

        except KeyboardInterrupt:
            self._logger.info('Closing %s' % self._uid)

        except Exception as e:
            self._logger.exception('WorkloadManager failed: %s' % e)

        finally:
            with self._rmq:
                self._rmq.delete()
