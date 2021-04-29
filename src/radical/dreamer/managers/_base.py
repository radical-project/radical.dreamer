
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

    def __init__(self, cfg=None, cfg_path=None, **kwargs):
        if not cfg and not cfg_path:
            # cfg = Config(from_dict={})
            raise Exception('Configuration is not set')
        elif not cfg and cfg_path:
            cfg = Config(cfg_path=cfg_path)
        else:
            cfg = Config(from_dict=cfg)

        self._uid = generate_id('rd.%s' % self._NAME, mode=ID_UNIQUE)
        self._logger = Logger(self._uid, ns='radical.dreamer')
        self._is_peer = bool(kwargs.get('is_peer', False))

        if not self._is_peer:
            self._rmq_setup(cfg)

        self._cfg_setup(cfg)

        self._logger.info('%s configuration is set' %
                          self._NAME.title().replace('_', ''))

    def _rmq_setup(self, cfg):
        rmq_url = os.environ.get('RADICAL_DREAMER_RMQ_URL') or cfg.rabbitmq.url
        self._rmq = None if not rmq_url else RabbitMQ(
            url=rmq_url,
            exchange=cfg.rabbitmq.exchange,
            queues=cfg.rabbitmq.queues)
        self._rmq_queues = cfg.rabbitmq.queues

    def _cfg_setup(self, cfg):
        pass
