
import random

from ...configs import ScheduleConfig


class Schedule:

    def __init__(self, cfg=None):
        if cfg and not isinstance(cfg, ScheduleConfig):
            raise Exception('Config not valid')

        self._cfg = cfg or ScheduleConfig()
        self._tasks = []

    @property
    def is_active(self):
        return bool(self._tasks)

    def reorder_cores(self, cores):
        """
        Re-order cores according to the defined strategy.

        :param cores: Core objects (radical.dreamer.units.core.Core).
        :type cores: list
        :return: Reordered Core objects (radical.dreamer.units.core.Core).
        :rtype: list
        """
        if self._cfg.strategy in ['largest_to_fastest',
                                  'smallest_to_fastest']:
            order_reverse = True
        elif self._cfg.strategy in ['largest_to_slowest',
                                    'smallest_to_slowest']:
            order_reverse = False
        else:
            # random strategy or FIFO (a.k.a. no strategy)
            order_reverse = None

        if order_reverse is None:
            if self._cfg.strategy == 'random':
                random.shuffle(cores)
        elif self._cfg.early_binding:
            cores.sort(key=lambda c: c.perf, reverse=order_reverse)
        else:
            if order_reverse:
                cores.sort(key=lambda c: (c.release_time, -c.perf))
            else:
                cores.sort(key=lambda c: (c.release_time, c.perf))

        return cores

    def reorder_tasks(self, tasks):
        """
        Re-order tasks according to the defined strategy.

        :param tasks: Task objects (radical.dreamer.units.task.Task).
        :type tasks: list
        :return: Reordered Task objects (radical.dreamer.units.task.Task).
        :rtype: list
        """
        if self._cfg.strategy in ['largest_to_fastest',
                                  'largest_to_slowest']:
            order_reverse = True
        elif self._cfg.strategy in ['smallest_to_fastest',
                                    'smallest_to_slowest']:
            order_reverse = False
        else:
            # random strategy or FIFO (a.k.a. no strategy)
            order_reverse = None

        if order_reverse is None:
            if self._cfg.strategy == 'random':
                random.shuffle(tasks)
        else:
            tasks.sort(key=lambda t: t.ops, reverse=order_reverse)

        return tasks

    def set_tasks(self, tasks):
        self._tasks = self.reorder_tasks(tasks=tasks)

    def get_scheduled_tasks(self, cores, **kwargs):
        output = []

        num_tasks = len(self._tasks)
        core_uids = [c.uid for c in self.reorder_cores(cores=cores)[:num_tasks]]

        if self._cfg.early_binding:

            num_cores = len(core_uids)

            if not self._tasks[0].core_uid:

                # initial binding for early-binding protocol
                for idx, task in enumerate(self._tasks):
                    task.core_uid = core_uids[idx % num_cores]

                output.extend(self._tasks[:num_cores])
                del self._tasks[:num_cores]

            else:

                idx = 0
                while True:

                    if self._tasks[idx].core_uid in core_uids:
                        output.append(self._tasks.pop(idx))
                    else:
                        idx += 1

                    if idx == len(self._tasks) or len(output) == num_cores:
                        break

        else:

            # late-binding protocol
            for core_uid in core_uids:
                self._tasks[0].core_uid = core_uid
                output.append(self._tasks.pop(0))

            # TODO: adaptive-binding protocol
            #       (additional data is in `kwargs`; input parameters will be
            #       extended with such additional data as planned release time
            #       per core and performance history per core)

        return output
