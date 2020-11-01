
import socket

from radical.utils import read_json, Munch

from ..utils import EnumTypes

BINDING_TYPE = EnumTypes(
    ('Early', 'early'),
    ('Late', 'late'),
    ('Dynamic', 'dynamic'),  # full knowledge about resource and workload
    ('None', 'none')         # zero-knowledge about resource and workload
)

try:
    import getpass
except ImportError:
    getpass = None

# UNIQ_ID should be in sync with all managers, thus all of them should be
# running under the same user account and at the same machine OR rabbitmq's
# exchange and queue names could be set by user in the corresponding config.
UNIQ_ID = '%s.%s' % ('nouser' if getpass is None else getpass.getuser(),
                     socket.gethostname())


class RMQQueueNames(Munch):
    _schema = {
        'allocation': str,
        'profile': str,
        'request': str,
        'resource': str,
        'schedule': str,
        'session': str,
        'workload': str
    }


class RMQConfig(Munch):
    _schema = {
        'url': str,
        'exchange': str,
        'queues': RMQQueueNames
    }


class SessionConfig(Munch):
    _schema = {
        'profile_base_name': str
    }


class ScheduleConfig(Munch):
    _schema = {
        'strategy': str,
        'early_binding': bool,
        'is_adaptive': bool
    }


class Config(Munch):

    """
    Base class to keep the config data.
    """

    _schema = {
        'rabbitmq': RMQConfig,
        'session': SessionConfig,
        'schedule': ScheduleConfig
    }

    _defaults = {
        'rabbitmq': {
            'url': 'amqp://localhost:5672/',
            'exchange': 'rd.%s' % UNIQ_ID,  # RMQ exchange
            'queues': {                     # RMQ queues/routing_keys
                'allocation': 'rd.allocation.%s' % UNIQ_ID,
                'profile': 'rd.profile.%s' % UNIQ_ID,
                'request': 'rd.request.%s' % UNIQ_ID,
                'resource': 'rd.resource.%s' % UNIQ_ID,
                'schedule': 'rd.schedule.%s' % UNIQ_ID,
                'session': 'rd.session.%s' % UNIQ_ID,
                'workload': 'rd.workload.%s' % UNIQ_ID
            }
        },
        'session': {
            'profile_base_name': 'rd.profile'
        },
        'schedule': {
            'strategy': '',
            'early_binding': True,
            'is_adaptive': False
        }
    }

    def __init__(self, from_dict=None, cfg_path=None):
        if not from_dict and cfg_path:
            from_dict = read_json(cfg_path)

        super().__init__(from_dict=from_dict)
