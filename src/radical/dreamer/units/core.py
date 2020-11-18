
from radical.utils import generate_id, Munch


class Core(Munch):

    _schema = {
        'uid': str,
        'perf': float,
        'perf_dynamic': float,
        'io_rate': float,
        'planned_release_time': float,
        'release_time': float
    }

    _defaults = {
        'uid': '',
        'perf': 1.,
        'perf_dynamic': 1.,
        'io_rate': 0.,
        'planned_release_time': 0.,
        'release_time': 0.
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

        # get core release time (from the previous task)
        task.start_time = self.release_time

        self.planned_release_time = task.start_time + (task.ops / self.perf)
        self.release_time += task.ops / self.perf_dynamic

        if self.io_rate:
            io_task_duration = task.ops / self.io_rate
            self.planned_release_time += io_task_duration
            self.release_time += io_task_duration

        # actual release time for the current task (dynamic performance)
        task.end_time = self.release_time

    # def is_busy(self, timestamp):
    #     # TODO: check exact time when is core considered as available/idle
    #     return timestamp < self.release_time
