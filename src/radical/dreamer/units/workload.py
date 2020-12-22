
from radical.utils import generate_id, Munch

from .task import Task
from .ext import SampleDistribution


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

    @property
    def tasks_list(self):
        return list(self.tasks.values())
