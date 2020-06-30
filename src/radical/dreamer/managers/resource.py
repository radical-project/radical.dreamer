
import json
import os

from radical.utils import write_json

from ..units import Core, Task

from ._base import Manager


class ResourceManager(Manager):

    _NAME = Manager.NAMES.Resource

    def __init__(self, cfg=None, cfg_path=None):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._sid = None
        self._profile_data = {}

    def run(self):
        try:
            with self._rmq:
                while True:
                    tasks = []

                    session_msg = self._rmq.get(self._rmq_queues.session)
                    if session_msg:
                        self._sid = json.loads(session_msg).get('sid')
                        self._logger.info('SessionID received: %s' % self._sid)

                    schedule_msg = self._rmq.get(self._rmq_queues.schedule)
                    if schedule_msg:
                        cores_dict = dict()
                        for s in json.loads(schedule_msg):
                            task = Task(**s['task'])
                            core = cores_dict.setdefault(
                                s['core']['uid'], Core(**s['core']))
                            core.execute(task)
                            tasks.append(task)
                        self._logger.info('Scheduled tasks are executed')

                        self._rmq.publish(self._rmq_queues.execute,
                                          json.dumps([c.as_dict() for c in
                                                      cores_dict.values()]))
                        self._logger.info('Result of execution is published')

                    if schedule_msg and self._sid:
                        self._set_profile(tasks=tasks)

        except KeyboardInterrupt:
            self._write_profile()
            self._logger.info('Closing %s' % self._uid)

        except Exception as e:
            self._logger.exception('ResourceManager failed: %s' % e)

        finally:
            with self._rmq:
                self._rmq.delete()

    def _set_profile(self, tasks):
        for task in tasks:
            self._profile_data.setdefault(self._sid, []).append({
                'task': task.uid,
                'ops': task.ops,
                'core': task.exec_core_id,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'exec_time': task.end_time - task.start_time})
        self._logger.info('Execution profile recorded')

    def _write_profile(self):
        file_name, file_ext = os.path.basename(
            self._cfg.output_profile).rsplit('.', 1)
        file_path = os.path.join(
            os.path.dirname(self._cfg.output_profile),
            '.'.join([file_name, self._uid, file_ext]))
        write_json(data=self._profile_data, fname=file_path)
        self._logger.info('Profile records from ResourceManager '
                          '%s are written to %s' % (self._uid, file_path))
