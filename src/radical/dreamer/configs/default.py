
from ._base import Config

try:
    import getpass
except ImportError:
    getpass = None

# this RAND_ID variable could be absolutely random string, it just have to
# be static to be in sync with all managers (Session, ResourceM.., WorkloadM..)
RAND_ID = '%s745' % ('' if getpass is None else getpass.getuser())
cfg_default = Config(from_dict={
    'rabbitmq': {
        'url': 'amqp://localhost:5672/',
        'exchange': 'rd_%s' % RAND_ID,  # RMQ exchange
        'queues': {                     # RMQ queues/routing_keys
            'allocation': 'allocation_%s' % RAND_ID,
            'request': 'request_%s' % RAND_ID,
            'resource': 'resource_%s' % RAND_ID,
            'schedule': 'schedule_%s' % RAND_ID,
            'session': 'session_%s' % RAND_ID,
            'workload': 'workload_%s' % RAND_ID
        }
    },
    'session': {
        'output_profile': './profile.json',
        'schedule_options': ['smallest_to_fastest'],
        'early_binding': True,
        'dynamic_resource': True
    }
})
