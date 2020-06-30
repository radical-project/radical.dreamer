
from radical.utils import generate_id, Munch


class Task(Munch):

    _schema = {
        'uid': str,
        'ops': float,
        'start_time': float,
        'end_time': float,
        'exec_core_id': str
    }

    _defaults = {
        'uid': '',
        'ops': 1.,
        'start_time': 0.,
        'end_time': 0.,
        'exec_core_id': ''
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=self._defaults)

        if kwargs:
            self.update(kwargs)

        if not self.uid:
            self.uid = generate_id('task')
