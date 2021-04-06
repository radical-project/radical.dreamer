
import os

from radical.utils import write_json, generate_id, ID_CUSTOM

from ..units import MultiResource, Resource, Workload

from .resource import ResourceManager
from .ext.schedule import Schedule

from ._base import Manager


class Session(Manager):

    _NAME = Manager.NAMES.Session

    def __init__(self, cfg=None, cfg_path=None, is_peer=False, **kwargs):
        super().__init__(cfg=cfg, cfg_path=cfg_path, is_peer=is_peer, **kwargs)

        self._resource = None
        self._workloads = []
        self._profile_data = {}

    def _cfg_setup(self, cfg):
        self._cfg = cfg.session

        if self._is_peer:
            self._schedule = Schedule(cfg=cfg.schedule)

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
        if self._resource is None or not self._workloads:
            raise Exception('Resource and/or Workload(s) are not set')

        # clean up profile data (i.e., profile per run)
        self._profile_data.clear()

        if not self._is_peer:
            self._run_as_client()
        else:
            self._run_as_peer()

        self._save_profile()

    def _run_as_client(self):
        with self._rmq:

            self._rmq.publish(queue=self._rmq_queues.resource,
                              data=self._resource.as_dict())

            while self._workloads:

                workload = self._workloads.pop(0)

                self._rmq.publish(queue=self._rmq_queues.workload,
                                  data=workload.as_dict())
                self._set_profile(workload_uid=workload.uid,
                                  tasks=self._rmq.collect(
                                      queue=self._rmq_queues.profile,
                                      count=workload.size))

    def _run_as_peer(self):
        while self._workloads:

            workload = self._workloads.pop(0)

            self._logger.info('Processing starts')
            processed_tasks = ResourceManager.processing(
                resource=self._resource,
                workload=workload,
                schedule=self._schedule)

            self._set_profile(workload_uid=workload.uid,
                              tasks=processed_tasks)

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
        self._logger.info('Save profile data records')
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
