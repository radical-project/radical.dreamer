
from radical.utils import generate_id, Munch

from ..utils import EnumTypes


class Core(Munch):

    STATES = EnumTypes(
        ('Idle', 0),
        ('Busy', 1),
        ('Offline', -1)
    )

    _schema = {
        'uid': str,
        'perf': float,
        'perf_dynamic': float,
        'perf_history': list,
        'io_rate': float,
        'acquire_time': float,
        'release_time': float,
        'planned_release_time': float,
        'planned_execute_time': float,
        'state': int
    }

    _defaults = {
        'uid': '',
        'perf': 1.,
        'perf_dynamic': 1.,
        'perf_history': [],
        'io_rate': 0.,
        'acquire_time': 0.,
        'release_time': 0.,
        'planned_release_time': 0.,
        'planned_execute_time': 0.,
        'state': STATES.Idle
    }

    def __init__(self, **kwargs):
        if 'perf_dynamic' not in kwargs and 'perf' in kwargs:
            kwargs['perf_dynamic'] = kwargs['perf']

        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('core')

    def execute(self, task):
        # resource.process does check of core_uid and task bound id.
        # if self.uid != task.core_uid:
        #     raise Exception('Task %s is not bound to Core %s' %
        #                     (task.uid, self.uid))

        # core's time of acquire is equal to the previous time of release
        self.acquire_time = self.release_time
        # task start time is the time of core got acquired
        task.start_time = self.acquire_time

        self.planned_execute_time = task.ops / self.perf
        self.release_time += task.ops / self.perf_dynamic

        if self.io_rate:
            io_task_duration = task.ops / self.io_rate
            self.planned_execute_time += io_task_duration
            self.release_time += io_task_duration

        # keep both values for planned release and execute times
        self.planned_release_time = task.start_time + self.planned_execute_time

        # actual release time for the current task (dynamic performance)
        task.end_time = self.release_time

        self.state = self.STATES.Busy
        return self

    def release(self):
        # keep history of actual core performances
        self.perf_history.append(self.perf_dynamic)

        self.planned_execute_time = 0.
        self.state = self.STATES.Idle
        return self

    @property
    def is_busy(self):
        return self.state == self.STATES.Busy

    # @property
    # def is_available(self):
    #     return self.state != self.STATES.Offline
