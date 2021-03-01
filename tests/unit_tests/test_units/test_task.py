
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import glob

import radical.utils as ru

from radical.dreamer.units import Task

from unittest import TestCase

TEST_CASES_PATH = 'tests/unit_tests/test_units/test_cases/task.*.json'


class TaskTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_cases = []
        for f in glob.glob(TEST_CASES_PATH):
            cls._test_cases.extend(ru.read_json(f))

    def test_init(self):

        # default attributes
        t = Task()

        self.assertTrue(t.uid.startswith('task.'))
        self.assertEqual(t.ops, 1.)
        self.assertEqual(t.start_time, 0.)
        self.assertEqual(t.end_time, 0.)
        self.assertFalse(t.core_uid)

        # with input data
        for test_case in self._test_cases:
            print(test_case)
            t = Task(**test_case['input'])

            result = dict(test_case['input'])
            for k, v in Task._defaults.items():
                if k not in result:
                    result[k] = v

            if result.get('uid'):
                self.assertEqual(t.uid, result['uid'])
            self.assertEqual(t.ops, result['ops'])
            self.assertEqual(t.start_time, result['start_time'])
            self.assertEqual(t.end_time, result['end_time'])
            self.assertEqual(t.core_uid, result['core_uid'])
