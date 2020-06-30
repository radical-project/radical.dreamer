
from radical.utils import generate_id, Munch

from .task import Task
from .ext import SampleDistribution


class Workload(Munch):

    _schema = {
        'uid': str,
        'tasks': list,
        'ops_dist': SampleDistribution
    }

    _defaults = {
        'uid': '',
        'tasks': []
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=self._defaults)

        if 'num_tasks' in kwargs:
            kwargs.setdefault('ops_dist', {})['size'] = kwargs['num_tasks']
            del kwargs['num_tasks']

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('workload')

        if not self.tasks:
            self.tasks = [Task(ops=abs(o)) for o in self.ops_dist.generate()]
        else:
            for idx in range(self.num_tasks):
                self.tasks[idx] = Task(**self.tasks[idx])

    @property
    def num_tasks(self):
        return len(self.tasks)

    def as_dict(self):
        output = super().as_dict()
        output['tasks'] = [t.as_dict() for t in self.tasks]
        return output

    def get_tasks(self, *args):
        """
        Get all [or subset] of tasks that are of a certain order (if no
        conditions are set then all tasks of a random order will be returned).

        :arg value "largest_first" - task with higher OPS goes first
        :arg value "smallest_first" - task with lower OPS goes first
        """
        if 'largest_first' in args:
            output = sorted(self.tasks, key=lambda t: t.ops, reverse=True)
        elif 'smallest_first' in args:
            output = sorted(self.tasks, key=lambda t: t.ops)
        else:
            from random import shuffle
            output = list(self.tasks)
            shuffle(output)
        return output
