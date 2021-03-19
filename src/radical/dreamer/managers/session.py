
import os

from radical.utils import write_json, generate_id, ID_CUSTOM

from ..units import MultiResource, Resource, Workload

from ._base import Manager


class Session(Manager):

    _NAME = Manager.NAMES.Session

    def __init__(self, cfg=None, cfg_path=None):
        super().__init__(cfg=cfg, cfg_path=cfg_path)

        self._resource = None
        self._workloads = []
        self._profile_data = {}

    def _cfg_setup(self, cfg):
        self._cfg = cfg.session

    def set(self, **kwargs):
        """
        Set descriptions of Resource and Workload(s).

        :keyword resource: Resource description.
                           radical.dreamer.units.(multi)resource.(Multi)Resource
        :keyword workload: Workload description.
                           radical.dreamer.units.workload.Workload
        :keyword workloads: List of workload descriptions
                            (mutually exclusive with `workload` input).
        """
        if kwargs.get('resource'):
            if not isinstance(kwargs['resource'], (Resource, MultiResource)):
                raise ValueError('Type of resource object is not valid')
            self._resource = kwargs['resource']

        if kwargs.get('workload'):
            if not isinstance(kwargs['workload'], Workload):
                raise ValueError('Type of workload object is not valid')
            self._workloads.append(kwargs['workload'])
        elif isinstance(kwargs.get('workloads'), (list, tuple)):
            for workload in kwargs['workloads']:
                self.set(workload=workload)

    def run(self):
        """
        Publish defined objects (resource and workloads) to RMQ and collect
        output profile data per run (profile data is grouped per workload).
        """
        # clean up profile data (i.e., profile per run)
        self._profile_data.clear()

        with self._rmq:

            if self._resource is None or not self._workloads:
                raise Exception('Resource and/or Workload(s) are not set')

            self._rmq.publish(queue=self._rmq_queues.resource,
                              data=self._resource.as_dict())

            while self._workloads:

                workload = self._workloads.pop(0)
                self._rmq.publish(queue=self._rmq_queues.workload,
                                  data=workload.as_dict())

                num_not_executed_tasks = workload.size
                while num_not_executed_tasks:

                    executed_tasks = self._rmq.get(self._rmq_queues.profile)
                    if not executed_tasks:
                        continue

                    self._set_profile(workload_uid=workload.uid,
                                      tasks=executed_tasks)
                    num_not_executed_tasks -= len(executed_tasks)

        self._save_profile()

    def _set_profile(self, workload_uid, tasks):
        for task in tasks:
            self._profile_data.setdefault(workload_uid, []).append({
                'task': task['uid'],
                'ops': task['ops'],
                'core': task['core_uid'],
                'start_time': task['start_time'],
                'end_time': task['end_time'],
                'exec_time': task['end_time'] - task['start_time']})

    def _save_profile(self):
        file_path = os.path.join(
            os.path.dirname(self._cfg.profile_base_name),
            '.'.join([os.path.basename(self._cfg.profile_base_name),
                      generate_id('%(date)s.%(counter)04d', mode=ID_CUSTOM),
                      'json']))
        file_name, file_ext = os.path.splitext(file_path)

        _idx = 0
        while os.path.exists(file_path):
            _idx += 1
            file_path = '%s_%s%s' % (file_name, _idx, file_ext)

        write_json(data=self._profile_data, fname=file_path)
        self._logger.info('Profile records saved to %s' % file_path)
