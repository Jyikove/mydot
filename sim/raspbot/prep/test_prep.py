import math
import unittest
from dataclasses import fields

from interface import Action, ActionLimits, Bounds, Observation, RGBFrame, SimClock
from scoring import Cylinder, Rectangle, score_goal


class InterfaceTests(unittest.TestCase):
    def test_accepts_bounds_and_keeps_units_in_distinct_fields(self):
        limits = ActionLimits(*(Bounds(-i, i) for i in range(1, 6)))
        action = Action(1, -2, 3, -4, 5)
        self.assertIs(limits.validate(action), action)

    def test_rejects_out_of_range_in_each_field(self):
        limits = ActionLimits(*(Bounds(-1, 1) for _ in range(5)))
        for i in range(5):
            values = [0] * 5
            values[i] = math.nextafter(1, math.inf)
            with self.subTest(i=i), self.assertRaises(ValueError):
                limits.validate(Action(*values))

    def test_rejects_nonfinite_and_non_numeric(self):
        for value in (math.nan, math.inf, -math.inf, True, "0"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Action(0, 0, 0, value, 0)
        with self.assertRaises(ValueError):
            Bounds(1, -1)

    def test_camera_interleaving_and_coincidence(self):
        clock = SimClock()
        windows = [clock.next_control() for _ in range(4)]
        self.assertEqual([(w.start_tick, w.end_tick) for w in windows],
                         [(0, 12), (12, 24), (24, 36), (36, 48)])
        self.assertEqual([w.camera_ticks for w in windows], [(), (16,), (32,), (48,)])

    def test_no_accumulated_timing_drift_and_reset(self):
        clock = SimClock()
        windows = [clock.next_control() for _ in range(2000)]
        self.assertEqual(windows[-1].time_s, 100)
        self.assertEqual([t for w in windows for t in w.camera_ticks], list(range(16, 24001, 16)))
        clock.reset()
        self.assertEqual(clock.tick, 0)
        self.assertEqual(clock.next_control(), windows[0])

    def test_default_observation_whitelist(self):
        self.assertEqual([field.name for field in fields(Observation)], ["tick", "onboard"])
        self.assertEqual([field.name for field in fields(RGBFrame)], ["tick", "width", "height", "data"])


class ScoringTests(unittest.TestCase):
    def test_upright_extent_and_full_goal(self):
        piece = Cylinder((2.85, 1, 0.05), (0, 0, 1), 0.05, 0.05)
        score = score_goal([piece])
        self.assertEqual(piece.xy_extent(), (0.05, 0.05))
        self.assertTrue(score.success)
        self.assertAlmostEqual(score.pieces[0].min_clearance, 0.10)

    def test_tilt_crosses_side_despite_center_inside(self):
        piece = Cylinder((2.85, 1, 0.2), (1, 0, 1), 0.10, 0.15)
        x, y = piece.xy_extent()
        self.assertAlmostEqual(x, 0.25 / math.sqrt(2))
        self.assertAlmostEqual(y, 0.10)
        self.assertLess(score_goal([piece]).pieces[0].right, 0)
        self.assertFalse(score_goal([piece]).success)

    def test_horizontal_axis_and_nearly_axis_aligned_axis(self):
        horizontal = Cylinder((0, 0, 0), (1, 0, 0), 0.25, 0.125)
        self.assertEqual(horizontal.xy_extent(), (0.125, 0.25))
        near_axis = Cylinder((0, 0, 0), (1, 1e-12, 0), 1e10, 0.125)
        self.assertAlmostEqual(near_axis.xy_extent()[0], 0.135)

    def test_sign_and_large_magnitude_of_axis_do_not_change_extent(self):
        def extent(axis):
            return Cylinder((0, 0, 0), axis, 0.25, 0.125).xy_extent()
        self.assertEqual(extent((1, 1, 0)), extent((-1e308, -1e308, 0)))
        self.assertEqual(extent((1, 1, 0)), extent((1e-308, 1e-308, 0)))

    def test_extent_matches_constructed_surface_extremes(self):
        piece = Cylinder((0, 0, 0), (2, -3, 6), 0.25, 0.125)
        u = tuple(component / 7 for component in piece.axis)
        for i, extent in enumerate(piece.xy_extent()):
            # Choose the top/bottom cap by sign, then construct a rim point
            # toward the coordinate axis in that cap's plane.
            p = [(i == j) - u[i] * u[j] for j in range(3)]
            norm = math.hypot(*p)
            rim = [piece.radius * value / norm for value in p]
            cap = [math.copysign(piece.half_height, u[i]) * value for value in u]
            self.assertAlmostEqual(cap[i] + rim[i], extent)

    def test_closed_rectangle_and_mixed_pieces(self):
        goal = Rectangle(Bounds(0, 1), Bounds(0, 1))
        touching = Cylinder((0.25, 0.75, 0), (0, 0, 1), 0.25, 0.125)
        outside = Cylinder((0.125, 0.75, 0), (0, 0, 1), 0.25, 0.125)
        score = score_goal([touching, outside], goal)
        self.assertEqual(score.pieces[0].min_clearance, 0)
        self.assertEqual((score.count, score.fraction, score.success), (1, 0.5, False))
        self.assertFalse(score_goal([], goal).success)

    def test_invalid_geometry(self):
        for axis, radius in [((0, 0, 0), 1), ((0, 0, 1), -1), ((0, 0, math.nan), 1)]:
            with self.subTest(axis=axis, radius=radius), self.assertRaises(ValueError):
                Cylinder((0, 0, 0), axis, radius, 1)


if __name__ == "__main__":
    unittest.main()
