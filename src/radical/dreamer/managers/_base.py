
import os

from radical.utils import generate_id, ID_UNIQUE, Logger

from ..configs import Config
from ..utils import EnumTypes, RabbitMQ


class Manager:

    _NAME = ''
    NAMES = EnumTypes(
        ('Session', 'session'),
        ('Resource', 'resource_manager'),
        ('Workload', 'workload_manager')
    )

    def __init__(self, cfg=None, cfg_path=None):
        self._uid = generate_id('rd.%s' % self._NAME, mode=ID_UNIQUE)
        self._logger = Logger(self._uid)

        if not cfg and not cfg_path:
            # cfg = Config(from_dict={})
            raise Exception('Configuration is not set.')
        elif not cfg and cfg_path:
            cfg = Config(cfg_path=cfg_path)
        self._logger.info('Configuration is set.')

        self._cfg = cfg.session
        self._rmq_queues = cfg.rabbitmq.queues

        self._rmq = RabbitMQ(
            url=os.environ.get('RADICAL_DREAMER_RMQ_URL') or cfg.rabbitmq.url,
            exchange=cfg.rabbitmq.exchange,
            queues=cfg.rabbitmq.queues)
