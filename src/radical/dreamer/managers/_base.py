
import os

from radical.utils import generate_id, Logger, ID_UNIQUE

from ..configs import Config
from ..utils import EnumTypes, RabbitMQ


class Manager:

    _NAME = ''
    NAMES = EnumTypes(
        ('Session', 'session'),
        ('Resource', 'resource_manager')
    )

    def __init__(self, cfg=None, cfg_path=None):
        self._uid = generate_id('rd.%s' % self._NAME, mode=ID_UNIQUE)
        self._logger = Logger(self._uid)

        if not cfg and not cfg_path:
            # cfg = Config(from_dict={})
            raise Exception('Configuration is not set')
        elif not cfg and cfg_path:
            cfg = Config(cfg_path=cfg_path)
        self._cfg_setup(cfg)
        self._logger.info('%s configuration is set' %
                          self._NAME.title().replace('_', ''))

        self._rmq_queues = cfg.rabbitmq.queues
        self._rmq = RabbitMQ(
            url=os.environ.get('RADICAL_DREAMER_RMQ_URL') or cfg.rabbitmq.url,
            exchange=cfg.rabbitmq.exchange,
            queues=cfg.rabbitmq.queues)

    def _cfg_setup(self, cfg):
        pass
