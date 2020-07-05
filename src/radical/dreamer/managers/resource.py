
import json
import os

from radical.utils import write_json

from ..units import MultiResource, Resource, Task

from ._base import Manager


class ResourceManager(Manager):

    _NAME = Manager.NAMES.Resource

    def __init__(self, cfg=None, cfg_path=None):
        super().__init__(cfg=cfg, cfg_path=cfg_path)
        with self._rmq:
            self._rmq.declare()

        self._sid = None
        self._resource = None
        self._profile_data = {}

    def _get_allocation_ids(self, num_cores):
        options = {'num': num_cores,
                   'prior_sort': False if self._cfg.early_binding else True}

        if ('largest_to_fastest' in self._cfg.schedule_options or
                'smallest_to_fastest' in self._cfg.schedule_options):
            options['mode'] = 'fastest_first'

        elif ('largest_to_slowest' in self._cfg.schedule_options or
                'smallest_to_slowest' in self._cfg.schedule_options):
            options['mode'] = 'slowest_first'

        output = []
        for core in self._resource.get_cores(**options):
            output.append(core.uid)
        return output

    def run(self):
        try:
            with self._rmq:
                while True:

                    session_msg = self._rmq.get(self._rmq_queues.session)
                    if session_msg:
                        session = json.loads(session_msg)
                        self._sid = session.get('sid')
                        if self._resource and session.get('new_resource'):
                            self._resource = None
                        self._logger.info('SessionID received: %s' % self._sid)

                    resource_msg = self._rmq.get(self._rmq_queues.resource)
                    if resource_msg:
                        resource = json.loads(resource_msg)
                        if resource['uid'].startswith('multi'):
                            self._resource = MultiResource(**resource)
                        else:
                            self._resource = Resource(**resource)
                        self._logger.info('Resource %s is received' %
                                          self._resource.uid)

                    if self._resource and self._sid:
                        tasks = []

                        num_cores = None
                        if self._cfg.early_binding:
                            _msg = None
                            while not _msg:
                                # get an allocation request from request-queue
                                _msg = self._rmq.get(self._rmq_queues.request)
                            num_cores = json.loads(_msg).get('num_cores')

                        # publish allocated "cores" to allocation-queue
                        self._rmq.publish(
                            self._rmq_queues.allocation,
                            json.dumps(self._get_allocation_ids(num_cores)))
                        self._logger.info('Allocation (uids) is published')

                        _msg = None
                        while not _msg:
                            # get scheduled tasks with cores from schedule-queue
                            _msg = self._rmq.get(self._rmq_queues.schedule)
                        # task-groups: [[{t0c0}, {t1c1}], [{t2c0}, {t3c1}]]
                        for group in json.loads(_msg):
                            for p in group:
                                task = Task(**p['task'])
                                self._resource.cores[p['core']].execute(task)
                                tasks.append(task)
                            # after all allocated cores processed another group
                            # of tasks, then check is resource dynamic (should
                            # cores performance be re-generated)
                            if self._cfg.dynamic_resource:
                                self._resource.generate_cores_perf()
                        self._logger.info('Scheduled tasks are executed')

                        self._set_profile(tasks=tasks)
                        self._sid = None

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
