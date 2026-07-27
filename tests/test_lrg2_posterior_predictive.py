#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))
import lrg2_posterior_predictive as P
import max_influence_mocks as M


class LRG2PosteriorPredictiveTests(unittest.TestCase):
    def test_observed_held_out_prediction(self):
        result = P.analyze_dataset(M.observed_data())
        self.assertTrue(result["converged"])
        self.assertFalse(result["near_prior_boundary"])
        self.assertAlmostEqual(result["chi2"], 6.2912, places=3)
        self.assertAlmostEqual(
            result["analytic_chi2_tail_probability"], 0.04304, places=4
        )
        self.assertAlmostEqual(
            result["alcock_paczynski_ratio"]["z_score"], 0.8843, places=3
        )
        self.assertAlmostEqual(
            result["isotropic_volume_distance"]["z_score"], -2.3194, places=3
        )

    def test_predictive_mock_is_deterministic(self):
        observed = P.analyze_dataset(M.observed_data())
        truth = observed["fit_without_lrg2"]["parameters"]
        first = P.make_mock(P.SEED_START, truth)
        second = P.make_mock(P.SEED_START, truth)
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        self.assertTrue((first[2] == second[2]).all())

    def test_prediction_covariance_is_included(self):
        result = P.analyze_dataset(M.observed_data())
        measurement = result["lrg2"]["measurement_covariance"]
        predictive = result["lrg2"]["prediction_covariance_laplace"]
        total = result["lrg2"]["total_covariance"]
        for row in range(2):
            for column in range(2):
                self.assertAlmostEqual(
                    total[row][column],
                    measurement[row][column] + predictive[row][column],
                    places=12,
                )


if __name__ == "__main__":
    unittest.main()
