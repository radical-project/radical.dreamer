
from ..units import MultiResource, Resource, Task, Workload

from ._base import Manager
from .ext import Schedule


class ResourceManager(Manager):

    _NAME = Manager.NAMES.Resource

    def __init__(self, cfg=None, cfg_path=None):
        Manager.__init__(self, cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._resource = None
        self._workload = None

    def _cfg_setup(self, cfg):
        self._schedule = Schedule(cfg=cfg.schedule)

    def _run(self):
        while True:

            # - keep it for later enhancements (e.g., config for Schedule) -
            # session = self._rmq.get(self._rmq_queues.session)
            # if session:
            # - read session data (e.g., configs) -

            if self._resource is None:
                resource = self._rmq.get(self._rmq_queues.resource)
                if resource:
                    if resource['uid'].startswith('multiresource'):
                        self._resource = MultiResource(**resource)
                    else:
                        self._resource = Resource(**resource)
                    self._logger.info('Resource (%s) received' %
                                      self._resource.uid)

            if self._workload is None:
                workload = self._rmq.get(self._rmq_queues.workload)
                if workload:
                    self._workload = Workload(**workload)
                    self._logger.info('Workload (%s) received' %
                                      self._workload.uid)

            # start to process

            if self._resource and self._workload:

                self._schedule.set_tasks(self._workload.tasks_list)

                for idle_cores in self._resource.idle_cores:

                    if not self._schedule.is_active:
                        if not self._resource.is_busy:
                            # exit processing (no new tasks, no busy cores)
                            break
                        else:
                            # emulate cycle(s) to release last busy cores
                            continue

                    tasks = self._schedule.get_scheduled_tasks(idle_cores)
                    self._resource.process(tasks)

                    # publish profile data back to the session [manager]
                    self._rmq.publish(
                        queue=self._rmq_queues.profile,
                        data=Task.demunch(tasks))

                self._workload = None
                self._logger.info('Scheduled tasks executed')

    def run(self):
        obj_name = self._NAME.title().replace('_', '')

        print('[INFO] Do not close until all sessions are processed\n'
              '[INFO] %s running...' % obj_name)

        try:
            with self._rmq:
                self._run()

        except KeyboardInterrupt:
            self._logger.info('%s terminated' % obj_name)

        except Exception as e:
            self._logger.exception('%s failed: %s' % (obj_name, e))

        finally:
            print('\n[INFO] %s stopped' % obj_name)
            with self._rmq:
                self._rmq.delete()
