
from radical.utils import generate_id, Munch


class Core(Munch):

    _schema = {
        'uid': str,
        'perf': float,
        'util': list,
        'task_history': list
    }

    _defaults = {
        'uid': '',
        'perf': 1.,
        'util': [],
        'task_history': []
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=self._defaults)

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('core')

    def execute(self, task):
        if self.util:
            task.start_time = self.util[-1][1]
        task.end_time = task.start_time + (task.ops / self.perf)

        self.util.append([task.start_time, task.end_time])
        self.task_history.append(task.uid)
        task.exec_core_id = self.uid
