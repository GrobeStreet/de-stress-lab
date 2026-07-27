#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
import max_influence_mocks as M
import time_variation_mocks as T


class TimeVariationTests(unittest.TestCase):
    def test_wa_transform_obeys_official_domain_and_is_invertible(self):
        for w0, wa in [(-1.0, 0.0), (-0.45, -1.7), (-2.5, 1.5), (0.5, -1.0)]:
            coordinate = T.coordinate_from_wa(w0, wa)
            recovered = T.wa_from_coordinate(w0, coordinate)
            self.assertAlmostEqual(recovered, wa, places=9)
            self.assertGreater(recovered, -3.0)
            self.assertLess(recovered, 2.0)
            self.assertLess(w0 + recovered, 0.0)

    def test_observed_direct_time_variation_fit(self):
        result = T.analyze_dataset(M.observed_data())
        self.assertTrue(result["converged"])
        self.assertFalse(result["near_prior_boundary"])
        self.assertAlmostEqual(result["constant_w"]["parameters"]["w0"], -1.03, places=2)
        self.assertAlmostEqual(result["evolving_w"]["parameters"]["w0"], -0.44, places=2)
        self.assertAlmostEqual(result["evolving_w"]["parameters"]["wa"], -1.68, places=2)
        self.assertGreater(result["test_statistic"], 7.5)
        self.assertLess(result["test_statistic"], 8.2)

    def test_lrg2_deletion_weakens_direct_time_variation(self):
        result = T.analyze_dataset(M.observed_data(), drop=2)
        self.assertTrue(result["converged"])
        self.assertEqual(result["dropped_tracer"], "LRG2 z=0.706")
        self.assertAlmostEqual(result["test_statistic"], 3.4263, places=3)

    def test_constant_w_mock_is_deterministic(self):
        observed = T.analyze_dataset(M.observed_data())
        truth = observed["constant_w"]["parameters"]
        first = T.make_mock(T.SEED_START, truth)
        second = T.make_mock(T.SEED_START, truth)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        self.assertTrue((first[2] == second[2]).all())


if __name__ == "__main__":
    unittest.main()
