# pylint: disable=unused-argument

__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import pika.exceptions

from radical.dreamer.configs import cfg_default
from radical.dreamer.managers import ResourceManager
from radical.dreamer.managers.ext import Schedule
from radical.dreamer.units import Resource, Workload

from unittest import TestCase, mock


class ResourceManagerTestClass(TestCase):

    @mock.patch('radical.dreamer.managers._base.generate_id', return_value='R0')
    @mock.patch('radical.dreamer.managers._base.Logger')
    def test_init(self, *args, **kwargs):

        with self.assertRaises(Exception):
            # no configuration set
            ResourceManager()

        with self.assertRaises(pika.exceptions.AMQPConnectionError):
            # no local RMQ running or no correct RMQ URL set
            ResourceManager(cfg=cfg_default)

    def test_processing(self):

        input_data = [Resource(), Workload(), Schedule()]
        for idx in range(len(input_data)):
            updated_input_data = list(input_data)
            updated_input_data[idx] = 'wrong_obj'
            with self.assertRaises(ValueError):
                ResourceManager.processing(*updated_input_data)
