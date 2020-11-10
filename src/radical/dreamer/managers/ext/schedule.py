
import itertools
import random

from ...configs import ScheduleConfig


def split_to_groups(data, size=None):
    size = size or len(data)
    return [data[i:i + size] for i in range(0, len(data), size)]


class Schedule:

    def __init__(self, cfg=None):
        if cfg and not isinstance(cfg, ScheduleConfig):
            raise Exception('Config not valid')

        self._cfg = cfg or ScheduleConfig()
        self._groups = []
        self._next_group_idx = 0

    @property
    def layout(self):
        return self._groups[:]

    @layout.setter
    def layout(self, value):
        self._groups = list(value)
        self._next_group_idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        output = self.next()
        if output is None:
            raise StopIteration
        return output

    def next(self):
        if self._next_group_idx < len(self._groups):
            output = self._groups[self._next_group_idx]
            self._next_group_idx += 1
        else:
            output = None
        return output

    def get_cores_filtered(self, resource, num_cores, uid_only=False):
        """
        Get all [or subset] of cores that are of a certain order (if no
        conditions are set then all cores of a random order will be returned).

        :param resource: Resource object.
        :type resource: radical.dreamer.units.(multi)resource.(Multi)Resource
        :param num_cores: Number of cores, if None then return all cores.
        :type num_cores: int/None
        :param uid_only: Flag to return only core uids.
        :type uid_only: bool
        :return: Cores (dicts or uids).
        :rtype: list
        """
        # binding type defines availability of knowledge about resource/cores
        prior_sort = False if self._cfg.early_binding else True

        # strategy uses knowledge about resource/cores to rearrange cores
        if self._cfg.strategy in ['largest_to_fastest',
                                  'smallest_to_fastest']:
            order_reverse = True
        elif self._cfg.strategy in ['largest_to_slowest',
                                    'smallest_to_slowest']:
            order_reverse = False
        else:
            # no strategy (FIFO) or random strategy
            order_reverse = None

        cores = list(resource.cores.values())
        if ((num_cores and num_cores < resource.num_cores and not prior_sort) or
                order_reverse is None):

            if self._cfg.strategy == 'random':
                random.shuffle(cores)

            cores = cores[:num_cores]

        if order_reverse is not None:
            cores.sort(key=lambda c: c.perf, reverse=order_reverse)

            if num_cores and prior_sort:
                cores = cores[:num_cores]

        return [c.uid if uid_only else c.as_dict() for c in cores]

    def get_tasks_grouped(self, workload, group_size):
        """
        Get all [or subset] of grouped tasks that are of a certain order (if no
        conditions are set then all tasks of a random order will be returned).

        :param workload: Workload object.
        :type workload: radical.dreamer.units.workload.Workload
        :param group_size: Number of tasks per group (to fit the resource).
        :type group_size: int/None
        :return: Groups of tasks (dict objects).
        :rtype: list
        """
        # binding type defines availability of knowledge about workload/tasks
        prior_sort = True if self._cfg.early_binding else False

        # strategy uses knowledge about workload/tasks to rearrange tasks
        if self._cfg.strategy in ['largest_to_fastest',
                                  'largest_to_slowest']:
            order_reverse = True
        elif self._cfg.strategy in ['smallest_to_fastest',
                                    'smallest_to_slowest']:
            order_reverse = False
        else:
            # no strategy (FIFO) or random strategy
            order_reverse = None

        tasks = list(workload.tasks.values())
        if ((group_size and group_size < workload.num_tasks and
                not prior_sort) or order_reverse is None):

            if self._cfg.strategy == 'random':
                random.shuffle(tasks)

            groups = split_to_groups(tasks, group_size)
        else:
            groups = [tasks]

        if order_reverse is not None:
            for idx in range(len(groups)):
                groups[idx].sort(key=lambda t: t.ops, reverse=order_reverse)

            if group_size and prior_sort:
                groups = split_to_groups(groups[0], group_size)

        return [[task.as_dict() for task in group] for group in groups]

    def binding(self, tasks_grouped, core_uids):
        for group in tasks_grouped:
            for idx in range(len(group)):
                # assign core_uid to the corresponding task
                group[idx]['core_uid'] = core_uids[idx]
            self._groups.append(group)

    def rebinding(self, core_uids):
        tasks = list(
            itertools.chain.from_iterable(self._groups[self._next_group_idx:]))
        del self._groups[self._next_group_idx:]

        # keep the same order of tasks
        tasks_grouped = split_to_groups(tasks, len(core_uids))
        self.binding(tasks_grouped, core_uids)

    def adaptive_binding(self, resource, num_cores):
        if not self._cfg.early_binding or self._cfg.is_adaptive:
            self.rebinding(
                core_uids=self.get_cores_filtered(
                    resource=resource,
                    num_cores=num_cores,
                    uid_only=True))
