
from radical.utils import generate_id

from ..utils import TypedDict


class Task(TypedDict):

    _schema = {
        'uid': str,
        'ops': float,
        'start_time': float,
        'end_time': float,
        'core_uid': str
    }

    _defaults = {
        'uid': '',
        'ops': 1.,
        'start_time': 0.,
        'end_time': 0.,
        'core_uid': ''
    }

    def __init__(self, **kwargs):
        super().__init__(from_dict=kwargs)

        if not self.uid:
            self.uid = generate_id('task')
