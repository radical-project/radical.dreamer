
from radical.utils import generate_id, Munch


class Core(Munch):

    _schema = {
        'uid': str,
        'perf': float,
        'io_rate': float,
        'task_exec_times': list,
        'task_uids': list
    }

    _defaults = {
        'uid': '',
        'perf': 1.,
        'io_rate': 0.,
        'task_exec_times': [],
        'task_uids': []
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('core')

    def run(self, task):
        # resource.process does make a check of core_uid and task bound id.
        # if self.uid != task.core_uid:
        #     raise Exception('Task %s is not bound to Core %s' %
        #                     (task.uid, self.uid))

        if self.task_exec_times:
            task.start_time = self.task_exec_times[-1][1]
        task.end_time = task.start_time + (task.ops / self.perf)

        if self.io_rate:
            task.end_time += task.ops / self.io_rate

        self.task_exec_times.append((task.start_time, task.end_time))
        self.task_uids.append(task.uid)

    @property
    def release_time(self):
        return 0. if not self.task_exec_times else self.task_exec_times[-1][1]

    # def is_busy(self, timestamp):
    #     # TODO: check exact time when is core considered as available/idle
    #     return timestamp < self.release_time
