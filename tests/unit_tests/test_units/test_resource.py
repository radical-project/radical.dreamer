
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import glob

import radical.utils as ru

from radical.dreamer.units import Core, Resource, Task
from radical.dreamer.units.ext import SampleDistribution

from unittest import TestCase

TEST_CASES_PATH = 'tests/unit_tests/test_units/test_cases/resource.*.json'


class ResourceTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_cases = []
        for f in glob.glob(TEST_CASES_PATH):
            cls._test_cases.extend(ru.read_json(f))

    def test_init(self):

        # default attributes
        r = Resource()

        self.assertTrue(r.uid.startswith('resource.'))
        self.assertIsInstance(r.cores, dict)
        self.assertIsInstance(r.cores_list[0], Core)
        self.assertIsInstance(r.perf_dist, SampleDistribution)
        self.assertEqual(r.io_rate, 0.)
        self.assertEqual(r.num_cores, 1)
        self.assertEqual(r.cores_list, r.next_idle_cores)
        self.assertFalse(r.is_busy)
        self.assertFalse(r.planned_release_times)

        # with input data
        for test_case in self._test_cases:

            r = Resource(**test_case['input'])

            if test_case['input'].get('uid'):
                self.assertEqual(r.uid, test_case['input']['uid'])

            if test_case['input'].get('io_rate'):
                self.assertEqual(r.io_rate, test_case['input']['io_rate'])

            if 'perf_dist' in test_case['input']:
                result = dict(test_case['input']['perf_dist'])
                for k, v in SampleDistribution._defaults.items():
                    if k not in result:
                        result[k] = v
                self.assertEqual(r.perf_dist.size, result['size'])
                self.assertEqual(r.perf_dist.name, result['name'])
                self.assertEqual(r.num_cores, result['size'])

            if test_case['input'].get('cores'):
                result = test_case['input']['cores']
                for uid, result_core in result.items():
                    self.assertEqual(r.cores[uid].uid, result_core['uid'])
                    self.assertEqual(r.cores[uid].perf, result_core['perf'])
                self.assertEqual(r.num_cores, len(result))

    def test_set_dynamic_performance(self):

        for test_case in self._test_cases:

            r = Resource(**test_case['input'])
            c = r.cores_list[0]

            r.set_dynamic_performance(core_uid=c.uid)

            # if temporal variation is not set, then `core.perf_dynamic`
            # will be equal to `core.perf`
            if not test_case['input'].get('perf_dist', {}).get('var_temporal'):
                self.assertEqual(c.perf, c.perf_dynamic)

            core_perf_dynamic_saved = c.perf_dynamic
            r.set_dynamic_performance(core_uid=c.uid)

            if not r.perf_dist.var_temporal:
                self.assertEqual(core_perf_dynamic_saved, c.perf_dynamic)
            else:
                self.assertNotEqual(core_perf_dynamic_saved, c.perf_dynamic)

    def test_process(self):

        for test_case in self._test_cases:

            if test_case.get('task', {}).get('core_uid'):

                r = Resource(**test_case['input'])
                t = Task(**test_case['task'])

                r.process(tasks=[t])

                if t.core_uid not in r.cores:
                    self.assertFalse(r.is_busy)
                    continue

                # core that executes task `t`
                c = r.cores[t.core_uid]

                self.assertTrue(c.is_busy)
                self.assertTrue(r.is_busy)
                self.assertEqual(len(r.planned_release_times), 1)

                core_perf_history_saved = r.cores_perf_history[c.uid]

                cores = r.next_idle_cores
                self.assertIn(c, cores)
                self.assertFalse(c.is_busy)
                self.assertFalse(r.is_busy)

                if not r.perf_dist.var_temporal:
                    self.assertEqual(core_perf_history_saved[-1],
                                     r.cores_perf_history[c.uid][-1])
                else:
                    self.assertNotEqual(core_perf_history_saved[-1],
                                        r.cores_perf_history[c.uid][-1])

            # FIXME: add a test case with multiple input tasks
            #        (check decreased value of performance in perf_history)
            # if test_case.get('tasks')
