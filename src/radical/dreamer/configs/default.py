
from ._base import Config


cfg_default = Config(from_dict={
    'rabbitmq': {
        'url': 'amqp://localhost:5672/'
    },
    'session': {
        'output_profile': './profile.json',
        'schedule_options': ['smallest_to_fastest'],
        'early_binding': True
    }
})
