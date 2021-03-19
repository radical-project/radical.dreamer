
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import glob

import radical.utils as ru

from radical.dreamer.units import Task, Workload
from radical.dreamer.units.ext import SampleDistribution

from unittest import TestCase

TEST_CASES_PATH = 'tests/unit_tests/test_units/test_cases/workload.*.json'


class WorkloadTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_cases = []
        for f in glob.glob(TEST_CASES_PATH):
            cls._test_cases.extend(ru.read_json(f))

    def test_init(self):

        # default attributes
        w = Workload()

        self.assertTrue(w.uid.startswith('workload.'))
        self.assertIsInstance(w.ops_dist, SampleDistribution)
        self.assertIsInstance(w.tasks, dict)
        self.assertEqual(w.num_tasks, 0)
        self.assertEqual(w.size, 1)

        w = Workload(set_tasks=True)

        self.assertEqual(w.num_tasks, 1)
        self.assertIsInstance(w.tasks_list[0], Task)

        # with input data
        for test_case in self._test_cases:

            w = Workload(**test_case['input'])

            if test_case['input'].get('uid'):
                self.assertEqual(w.uid, test_case['input']['uid'])

            if 'ops_dist' in test_case['input']:
                result = dict(test_case['input']['ops_dist'])
                for k, v in SampleDistribution._defaults.items():
                    if k not in result:
                        result[k] = v
                self.assertEqual(w.num_tasks, result['size'])
                self.assertEqual(w.size, result['size'])
                self.assertEqual(w.ops_dist.size, result['size'])
                self.assertEqual(w.ops_dist.name, result['name'])

            if test_case['input'].get('tasks'):
                result = test_case['input']['tasks']
                for uid, result_task in result.items():
                    self.assertEqual(w.tasks[uid].uid, result_task['uid'])
                    self.assertEqual(w.tasks[uid].ops, result_task['ops'])
                self.assertEqual(w.num_tasks, len(result))
