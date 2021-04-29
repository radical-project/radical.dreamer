# pylint: disable=unused-argument

__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

from radical.dreamer.configs import cfg_default
from radical.dreamer.managers import Session

from unittest import TestCase, mock


class SessionTestClass(TestCase):

    @mock.patch('radical.dreamer.managers._base.generate_id', return_value='S0')
    @mock.patch('radical.dreamer.managers._base.Logger')
    def test_init(self, *args, **kwargs):

        with self.assertRaises(Exception):
            # no configuration set
            Session()

        # default attributes for Session in a "peer" mode (no RMQ)
        s = Session(cfg=cfg_default, is_peer=True)

        with self.assertRaises(ValueError):
            s.set(resource='wrong_resource_obj')

        with self.assertRaises(ValueError):
            s.set(workload='wrong_workload_obj')
