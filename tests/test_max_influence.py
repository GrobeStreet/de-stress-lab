#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

import numpy as np


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
import max_influence_mocks as M


class MaximumInfluenceTests(unittest.TestCase):
    def test_whitened_residuals_equal_direct_chi2(self):
        dataset = M.observed_data()
        points = [
            (np.array([0.30, 0.68, 0.0222]), -1.0, 0.0),
            (np.array([0.35, 0.64, 0.0222]), -0.45, -1.7),
        ]
        for parameters, w0, wa in points:
            for drop in [None, 0, 2, 6]:
                direct = M.chi2_dataset(parameters, w0, wa, dataset, drop)
                residuals = M.residuals_dataset(parameters, w0, wa, dataset, drop)
                self.assertAlmostEqual(direct, float(residuals @ residuals), places=9)

    def test_observed_fit_reproduces_legacy_pipeline(self):
        result = M.analyze_dataset(M.observed_data(), "least-squares")
        self.assertTrue(result["converged"])
        self.assertEqual(result["selected_tracer"], "LRG2 z=0.706")
        self.assertAlmostEqual(result["dchi2_full"], -8.4575, places=3)
        self.assertAlmostEqual(result["dchi2_deleted"][2], -4.3326, places=3)
        self.assertAlmostEqual(result["max_influence"], 4.1249, places=3)

    def test_mock_is_deterministic(self):
        first = M.make_mock(10_000)
        second = M.make_mock(10_000)
        self.assertEqual(first[0], second[0])
        np.testing.assert_array_equal(first[1], second[1])
        np.testing.assert_array_equal(first[2], second[2])


if __name__ == "__main__":
    unittest.main()
