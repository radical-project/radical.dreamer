
import math

from ..units import MultiResource, Resource, Workload
from ..utils import as_dict

from ._base import Manager
from .ext import Schedule

PROFILE_MSG_SIZE = 1000


class ResourceManager(Manager):

    _NAME = Manager.NAMES.Resource

    def __init__(self, cfg=None, cfg_path=None, **kwargs):
        super().__init__(cfg=cfg, cfg_path=cfg_path, **kwargs)
        with self._rmq:
            self._rmq.declare()

        self._resource = None
        self._workload = None

    def _cfg_setup(self, cfg):
        self._schedule = Schedule(cfg=cfg.schedule)

    def run(self):
        obj_name = self._NAME.title().replace('_', '')
        print('[INFO] Do not close until all sessions are processed\n'
              '[INFO] %s running...' % obj_name)

        try:
            while True:

                # get Resource and Workload from RMQ
                self._logger.info('Waiting for inputs (Resource & Workload)')
                self.prepare_inputs()

                self._logger.info('Processing starts')
                processed_tasks = self.processing(resource=self._resource,
                                                  workload=self._workload,
                                                  schedule=self._schedule)

                # send processed tasks back to the session (profile records)
                self._logger.info('Publish profile data records')
                self.publish_profile_data(tasks=processed_tasks)

        except KeyboardInterrupt:
            self._logger.info('%s terminated' % obj_name)

        except Exception as e:
            self._logger.exception('%s failed: %s' % (obj_name, e))

        finally:
            print('\n[INFO] %s stopped' % obj_name)
            with self._rmq:
                self._rmq.delete()

    def prepare_inputs(self):
        self._workload = None
        with self._rmq:
            while True:

                # - keep it for later enhancements (e.g., config for Schedule) -
                # session = self._rmq.get(self._rmq_queues.session)
                # if session:
                # - read session data (e.g., configs) -

                if self._workload is None:
                    workload = self._rmq.get(self._rmq_queues.workload)
                    if not workload:
                        continue
                    self._workload = workload
                    self._logger.info('Workload-%s received' % workload['uid'])

                resource = self._rmq.get(self._rmq_queues.resource)
                if resource:
                    self._resource = resource
                    self._logger.info('Resource-%s received' % resource['uid'])

                if self._resource:
                    break

        self._workload = Workload(**self._workload)
        if self._resource['uid'].startswith('multiresource'):
            self._resource = MultiResource(**self._resource)
        else:
            self._resource = Resource(**self._resource)

    @staticmethod
    def processing(resource, workload, schedule):
        if not isinstance(resource, (Resource, MultiResource)):
            raise ValueError('[Multi]Resource type not valid')
        elif not isinstance(workload, Workload):
            raise ValueError('Workload type not valid')
        elif not isinstance(schedule, Schedule):
            raise ValueError('Schedule type not valid')

        if not resource.num_cores:
            resource.set_cores()

        if not workload.num_tasks:
            workload.set_tasks()

        # collect processed tasks (for profile records)
        output = []

        # prepare Schedule with input tasks (from Workload)
        schedule.set_tasks(workload.tasks_list)

        # start the processing
        while True:

            idle_cores = resource.next_idle_cores

            if not schedule.is_active:
                if not resource.is_busy:
                    # exit processing (no new tasks, no busy cores)
                    break
                else:
                    # emulate cycle(s) to release last busy cores
                    continue

            tasks = schedule.get_scheduled_tasks(idle_cores)
            resource.process(tasks)
            output.extend(tasks)

        return output

    def publish_profile_data(self, tasks):
        with self._rmq:

            # profile records are packed into messages
            num_msgs = math.ceil(len(tasks) / PROFILE_MSG_SIZE)
            for idx in range(num_msgs):
                # publish profile data
                self._rmq.publish(
                    queue=self._rmq_queues.profile,
                    data=as_dict(tasks[idx * PROFILE_MSG_SIZE:
                                       (idx + 1) * PROFILE_MSG_SIZE]))
