import math
import unittest


class JointUtilsTest(unittest.TestCase):
    def _utils(self):
        try:
            from ur3e_omniverse_bridge import joint_utils
        except ImportError as exc:
            self.fail(f"joint_utils module is missing: {exc}")
        return joint_utils

    def test_resolves_standard_ur3e_joint_names(self):
        joint_utils = self._utils()

        self.assertEqual(
            joint_utils.resolve_joint_names("ros"),
            [
                "shoulder_pan_joint",
                "shoulder_lift_joint",
                "elbow_joint",
                "wrist_1_joint",
                "wrist_2_joint",
                "wrist_3_joint",
            ],
        )

    def test_resolves_short_usd_joint_names(self):
        joint_utils = self._utils()

        self.assertEqual(
            joint_utils.resolve_joint_names("usd_short"),
            ["shoulder", "upper_arm", "elbow", "wrist_1", "wrist_2", "wrist_3"],
        )

    def test_generates_bounded_demo_motion_for_each_joint(self):
        joint_utils = self._utils()

        positions = joint_utils.sine_positions(
            elapsed_seconds=0.75,
            joint_count=6,
            amplitude=0.3,
            speed=0.8,
        )

        self.assertEqual(len(positions), 6)
        for value in positions:
            self.assertLessEqual(abs(value), 0.3 + 1e-9)
            self.assertTrue(math.isfinite(value))

    def test_maps_external_joint_positions_to_target_order(self):
        joint_utils = self._utils()

        target_names, target_positions = joint_utils.map_joint_positions(
            incoming_names=["elbow_joint", "shoulder_pan_joint", "wrist_1_joint"],
            incoming_positions=[2.0, 1.0, 3.0],
            source_names=["shoulder_pan_joint", "elbow_joint", "wrist_1_joint"],
            target_names=["shoulder", "elbow", "wrist_1"],
        )

        self.assertEqual(target_names, ["shoulder", "elbow", "wrist_1"])
        self.assertEqual(target_positions, [1.0, 2.0, 3.0])

    def test_resolves_http_payload_with_position_map(self):
        joint_utils = self._utils()

        names, positions = joint_utils.joint_payload_to_names_positions(
            payload={
                "positions": {
                    "shoulder_pan_joint": 0.1,
                    "shoulder_lift_joint": -1.0,
                    "elbow_joint": 1.2,
                }
            },
            default_names=["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint"],
        )

        self.assertEqual(names, ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint"])
        self.assertEqual(positions, [0.1, -1.0, 1.2])


if __name__ == "__main__":
    unittest.main()
