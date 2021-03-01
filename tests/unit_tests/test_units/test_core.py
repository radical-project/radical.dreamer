
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import glob

import radical.utils as ru

from radical.dreamer.units import Core, Task

from unittest import TestCase

TEST_CASES_PATH = 'tests/unit_tests/test_units/test_cases/core.*.json'


class CoreTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_cases = []
        for f in glob.glob(TEST_CASES_PATH):
            cls._test_cases.extend(ru.read_json(f))

    def test_init(self):

        # default attributes
        c = Core()

        self.assertTrue(c.uid.startswith('core.'))
        self.assertEqual(c.perf, 1.)
        self.assertEqual(c.perf_dynamic, 1.)
        self.assertFalse(c.perf_history)
        self.assertIsInstance(c.perf_history, list)
        self.assertEqual(c.io_rate, 0.)
        self.assertEqual(c.planned_release_time, 0.)
        self.assertEqual(c.release_time, 0.)
        self.assertEqual(c.state, Core.STATES.Idle)

        # with input data
        for test_case in self._test_cases:

            c = Core(**test_case['input'])

            result = dict(test_case['input'])
            for k, v in Core._defaults.items():
                if k not in result:
                    result[k] = v

            if result.get('uid'):
                self.assertEqual(c.uid, result['uid'])
            self.assertEqual(c.perf, result['perf'])
            self.assertEqual(c.perf_dynamic, result['perf_dynamic'])
            self.assertEqual(c.perf_history, result['perf_history'])
            self.assertEqual(c.io_rate, result['io_rate'])
            self.assertEqual(c.planned_release_time,
                             result['planned_release_time'])
            self.assertEqual(c.release_time, result['release_time'])
            self.assertEqual(c.state, result['state'])

    def test_execute(self):

        for test_case in self._test_cases:

            if 'task' not in test_case and 'result_execute' not in test_case:
                continue

            t = Task(**test_case['task'])
            c = Core(**test_case['input'])

            previous_release_time = c.release_time
            ret_c = c.execute(task=t)

            result = test_case['result_execute']
            self.assertIsInstance(ret_c, Core)
            self.assertEqual(ret_c.planned_release_time,
                             result['planned_release_time'])
            self.assertEqual(ret_c.release_time, result['release_time'])
            self.assertTrue(ret_c.is_busy)

            self.assertEqual(t.start_time, previous_release_time)
            self.assertEqual(t.end_time, ret_c.release_time)

    def test_release(self):

        for test_case in self._test_cases:

            if 'task' not in test_case:
                continue

            t = Task(**test_case['task'])
            c = Core(**test_case['input'])

            c.execute(task=t)
            perf_history_len = len(c.perf_history)
            self.assertEqual(c.state, Core.STATES.Busy)

            ret_c = c.release()
            self.assertIsInstance(ret_c, Core)
            self.assertEqual(ret_c.perf_dynamic, ret_c.perf_history[-1])
            self.assertEqual(len(ret_c.perf_history), perf_history_len + 1)
            self.assertFalse(ret_c.is_busy)
