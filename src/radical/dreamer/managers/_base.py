
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


class ManagerRunMixin:

    def run(self):
        obj_name = self._NAME.title().replace('_', '')

        print('[INFO] Do not close until all sessions are processed\n'
              '[INFO] %s running...' % obj_name)

        try:
            with self._rmq:

                # method should be overwritten
                self._run()

        except KeyboardInterrupt:
            self._logger.info('%s terminated' % obj_name)

        except Exception as e:
            self._logger.exception('%s failed: %s' % (obj_name, e))

        finally:
            print('\n[INFO] %s stopped' % obj_name)
            with self._rmq:
                self._rmq.delete()

    def _run(self):
        pass
