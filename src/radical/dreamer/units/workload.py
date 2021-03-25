
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

    def __init__(self, set_tasks=False, **kwargs):
        kwargs.setdefault('ops_dist', {})

        if 'num_tasks' in kwargs:
            kwargs['ops_dist']['size'] = kwargs['num_tasks']
            del kwargs['num_tasks']

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('workload')

        if set_tasks or self.tasks:
            self.set_tasks(tasks=self.tasks)

    def set_tasks(self, tasks=None):
        """
        [Re]generate Task objects.

        @param tasks: Tasks descriptions.
        @type tasks: dict/None
        """
        if not tasks:
            self.tasks.clear()
            for o in self.ops_dist.samples:
                task = Task(ops=abs(o))
                self.tasks[task.uid] = task
        else:
            self.tasks = {uid: Task(**task) for uid, task in tasks.items()}
            self.ops_dist.size = self.num_tasks

    @property
    def size(self):
        return self.ops_dist.size

    @property
    def num_tasks(self):
        return len(self.tasks)

    @property
    def tasks_list(self):
        return list(self.tasks.values())
