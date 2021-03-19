
__copyright__ = 'Copyright 2021, The RADICAL-Cybertools Team'
__license__   = 'MIT'

import glob

import radical.utils as ru

from radical.dreamer.units import MultiResource, Resource

from unittest import TestCase

TEST_CASES_PATH = 'tests/unit_tests/test_units/test_cases/multiresource.*.json'


class MultiResourceTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._test_cases = []
        for f in glob.glob(TEST_CASES_PATH):
            cls._test_cases.extend(ru.read_json(f))

    def test_init(self):

        with self.assertRaises(Exception):
            _ = MultiResource(resources=None)

        with self.assertRaises(Exception):
            _ = MultiResource(resources='wrong_resource')

        # default attributes
        mr = MultiResource(resources=[{}])

        self.assertTrue(mr.uid.startswith('multiresource.'))
        self.assertIsInstance(mr.cores, dict)
        self.assertIsInstance(mr.resources, list)
        self.assertIsInstance(mr.resources[0].cores, dict)
        self.assertEqual(len(mr.resources), 1)
        self.assertEqual(mr.num_cores, 0)
        self.assertEqual(mr.size, 1)

        mr = MultiResource(resources=[{}], set_cores=True)

        self.assertEqual(mr.num_cores, 1)

        # with input data
        for test_case in self._test_cases:

            if not isinstance(test_case['input'].get('resources'), list):
                continue

            resources = [Resource(**d) for d in test_case['input']['resources']]
            cores = {}
            for r in resources:
                cores.update(r.cores)

            mr = MultiResource(**test_case['input'])

            self.assertEqual(mr.num_cores, len(cores))
            self.assertEqual(len(mr.resources), len(resources))

            # check Cores duplication between Resources
            if len(resources) > 1:
                resources[1].cores = resources[0].cores
                with self.assertRaises(Exception):
                    _ = MultiResource(resources=resources)

    def test_set_dynamic_performance(self):

        for test_case in self._test_cases:

            if not isinstance(test_case['input'].get('resources'), list):
                continue

            mr = MultiResource(**test_case['input'])
            c = mr.cores_list[0]

            r = None
            for _r in mr.resources:
                if c.uid in _r.cores:
                    r = _r
                    break

            mr.set_dynamic_performance(core_uid=c.uid)

            # same approach as for Resource unit

            if not r.perf_dist.var_temporal:
                self.assertEqual(c.perf, c.perf_dynamic)

            core_perf_dynamic_saved = c.perf_dynamic
            mr.set_dynamic_performance(core_uid=c.uid)

            if not r.perf_dist.var_temporal:
                self.assertEqual(core_perf_dynamic_saved, c.perf_dynamic)
            else:
                self.assertNotEqual(core_perf_dynamic_saved, c.perf_dynamic)
