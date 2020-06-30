
import json

from radical.utils import Munch


class _RMQQueues(Munch):
    _schema = {
        'execute': str,
        'resource': str,
        'schedule': str,
        'session': str,
        'workload': str
    }


class _RMQConfig(Munch):
    _schema = {
        'url': str,
        'exchange': str,
        'queues': _RMQQueues
    }


class _SessionConfig(Munch):
    _schema = {
        'output_profile': str,
        'schedule_options': list,
        'early_binding': bool,
        'dynamic_resource': bool
    }


class Config(Munch):

    """
    Base class to keep the config data.
    """

    _schema = {
        'rabbitmq': _RMQConfig,
        'session': _SessionConfig
    }

    _defaults = {
        'rabbitmq': {
            'url': 'amqp://localhost:5672/',
            'exchange': 'rd',  # RMQ exchange
            'queues': {        # RMQ queues/routing_keys
                'execute': 'execute',
                'resource': 'resource',
                'schedule': 'schedule',
                'session': 'session',
                'workload': 'workload'
            }
        },
        'session': {
            'output_profile': 'profile.json',
            'schedule_options': [],
            'early_binding': True,
            'dynamic_resource': False
        }
    }

    def __init__(self, from_dict=None, cfg_path=None):
        super().__init__(from_dict=self._defaults)

        if from_dict:
            self.update(from_dict)
        elif cfg_path:
            with open(cfg_path) as f:
                self.update(json.loads(f.read()))
