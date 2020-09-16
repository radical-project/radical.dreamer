
import random

from radical.utils import generate_id, Munch

from .task import Task
from .ext import SampleDistribution


def split_to_groups(data, size=None):
    size = size or len(data)
    return [data[i:i + size] for i in range(0, len(data), size)]


class Workload(Munch):

    _schema = {
        'uid': str,
        'tasks': dict,
        'ops_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'tasks': {}
    }

    def __init__(self, **kwargs):
        if 'num_tasks' in kwargs:
            kwargs.setdefault('ops_dist', {})['size'] = kwargs['num_tasks']
            del kwargs['num_tasks']

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('workload')

        if not self.tasks:
            for o in self.ops_dist.samples:
                task = Task(ops=abs(o))
                self.tasks[task.uid] = task
        else:
            for uid in self.tasks:
                self.tasks[uid] = Task(**self.tasks[uid])

    @property
    def num_tasks(self):
        return len(self.tasks)

    def as_dict(self):
        output = super().as_dict()
        for uid in output['tasks']:
            output['tasks'][uid] = output['tasks'][uid].as_dict()
        return output

    def get_task_groups(self, group_size=None, order_reverse=None,
                        prior_sort=False):
        """
        Get all [or subset] of grouped tasks that are of a certain order (if no
        conditions are set then all tasks of a random order will be returned).

        :param group_size: Number of tasks per group (to fit the resource).
        :type group_size: int/None
        :param order_reverse: Sorting direction.
        :type order_reverse: bool/None
        :param prior_sort: Flag to pick prior sorted tasks (early-binding).
        :type prior_sort: bool
        :return: Groups of task objects.
        :rtype: list
        """
        tasks = list(self.tasks.values())
        if ((group_size and group_size < self.num_tasks and not prior_sort) or
                order_reverse is None):
            random.shuffle(tasks)
            output = split_to_groups(tasks, group_size)
        else:
            output = [tasks]

        if order_reverse is not None:
            for idx in range(len(output)):
                output[idx].sort(key=lambda t: t.ops, reverse=order_reverse)

            if group_size and prior_sort:
                output = split_to_groups(output[0], group_size)

        return output
