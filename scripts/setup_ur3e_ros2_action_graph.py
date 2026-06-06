from pathlib import Path
import asyncio
import os
import sys

import omni.graph.core as og
import omni.kit.app
import omni.timeline
import omni.usd
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics
import usdrt


REPO_ROOT = Path(__file__).resolve().parents[1]
ISAACSIM_ENV = Path(os.environ.get("ISAACSIM_ENV", Path.home() / "isaacsim-5.1.0"))
ROS_DISTRO = os.environ.get("ROS_DISTRO", "jazzy")
ISAAC_ROS_PYTHON = ISAACSIM_ENV / "lib" / "python3.11" / "site-packages" / "isaacsim" / "exts" / "isaacsim.ros2.bridge" / ROS_DISTRO / "rclpy"
UR3E_STAGE = Path(os.environ.get("ROBOTX_STAGE_PATH", REPO_ROOT / "assets" / "ur3e" / "ur3e.usd")).expanduser()
GRAPH_PATH = "/ActionGraph"
ROBOT_STAGE_PATH = "/ur3e"
COMMAND_TOPIC = "/joint_command"
STATE_TOPIC = "/joint_states"
CLOCK_TOPIC = "/clock"
PICK_PLACE_TOPIC = "/pick_place_command"
WORKSPACE_PATH = "/DemoScene/workspace"
PICK_PLACE_OBJECTS = {
    "pick_cube_red": f"{WORKSPACE_PATH}/pick_cube_red",
    "pick_cube_blue": f"{WORKSPACE_PATH}/pick_cube_blue",
}
END_EFFECTOR_NAME_HINTS = ("tool0", "tcp", "ee", "flange", "wrist_3", "wrist_3_link")
GRASP_OFFSET = Gf.Vec3d(0.0, 0.0, 0.0)


async def setup_ur3e_ros2_action_graph():
    app = omni.kit.app.get_app()
    # Full UI startup can still be initializing immediately after --exec runs.
    # Waiting a few frames avoids opening the stage while UI/viewport services
    # are still finishing startup.
    for _ in range(240):
        await app.next_update_async()

    result = await omni.usd.get_context().open_stage_async(str(UR3E_STAGE))
    print(f"[robotx] Opened UR3e stage: {UR3E_STAGE} result={result}")
    for _ in range(5):
        await app.next_update_async()

    stage = omni.usd.get_context().get_stage()
    robot_path = find_articulation_root_path(stage)
    print(f"[robotx] Using UR3e articulation root: {robot_path}")

    if stage.GetPrimAtPath(GRAPH_PATH):
        stage.RemovePrim(Sdf.Path(GRAPH_PATH))
        await app.next_update_async()

    og.Controller.edit(
        {"graph_path": GRAPH_PATH, "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
                ("SubscribeJointState", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
                ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "PublishJointState.inputs:execIn"),
                ("OnPlaybackTick.outputs:tick", "SubscribeJointState.inputs:execIn"),
                ("OnPlaybackTick.outputs:tick", "PublishClock.inputs:execIn"),
                ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                ("Context.outputs:context", "PublishJointState.inputs:context"),
                ("Context.outputs:context", "SubscribeJointState.inputs:context"),
                ("Context.outputs:context", "PublishClock.inputs:context"),
                ("ReadSimTime.outputs:simulationTime", "PublishJointState.inputs:timeStamp"),
                ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                ("SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
                ("SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
                ("SubscribeJointState.outputs:velocityCommand", "ArticulationController.inputs:velocityCommand"),
                ("SubscribeJointState.outputs:effortCommand", "ArticulationController.inputs:effortCommand"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("ArticulationController.inputs:robotPath", robot_path),
                ("SubscribeJointState.inputs:topicName", COMMAND_TOPIC),
                ("PublishJointState.inputs:topicName", STATE_TOPIC),
                ("PublishJointState.inputs:targetPrim", [usdrt.Sdf.Path(robot_path)]),
                ("PublishClock.inputs:topicName", CLOCK_TOPIC),
            ],
        },
    )

    for _ in range(5):
        await app.next_update_async()
    omni.timeline.get_timeline_interface().play()
    pick_place_controller = PickPlaceObjectController(stage, robot_path)
    await pick_place_controller.start()
    print(
        "[robotx] ROS 2 Action Graph ready: "
        f"{COMMAND_TOPIC} -> {robot_path}, publishing {STATE_TOPIC} and {CLOCK_TOPIC}"
    )


def find_articulation_root_path(stage):
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            return str(prim.GetPath())

    if stage.GetPrimAtPath(ROBOT_STAGE_PATH):
        return ROBOT_STAGE_PATH

    raise RuntimeError(f"Could not find UR3e articulation root in {UR3E_STAGE}")


class PickPlaceObjectController:
    def __init__(self, stage, robot_path: str):
        self.stage = stage
        self.robot_path = robot_path
        self.node = None
        self.rclpy = None
        self.attached_object_name = None
        self.end_effector_path = find_end_effector_path(stage, ROBOT_STAGE_PATH)
        print(f"[robotx] Pick/place end-effector prim: {self.end_effector_path}")

    async def start(self):
        if not ISAAC_ROS_PYTHON.exists():
            print(f"[robotx] Pick/place ROS Python path not found: {ISAAC_ROS_PYTHON}")
            return

        sys.path.insert(0, str(ISAAC_ROS_PYTHON))
        import rclpy
        from std_msgs.msg import String

        self.rclpy = rclpy
        if not rclpy.ok():
            rclpy.init(args=None)

        self.node = rclpy.create_node("isaac_pick_place_controller")
        self.node.create_subscription(String, PICK_PLACE_TOPIC, self.handle_command, 10)
        print(f"[robotx] Pick/place controller subscribed to {PICK_PLACE_TOPIC}")
        asyncio.ensure_future(self.update_loop())

    async def update_loop(self):
        app = omni.kit.app.get_app()
        while True:
            if self.node is not None:
                try:
                    self.rclpy.spin_once(self.node, timeout_sec=0.0)
                except Exception as exc:
                    print(f"[robotx] Pick/place update loop stopped: {exc}")
                    return
            self.update_attached_object()
            await app.next_update_async()

    def handle_command(self, message):
        action, _, object_name = message.data.partition(":")
        action = action.strip().lower()
        object_name = object_name.strip()
        if object_name not in PICK_PLACE_OBJECTS:
            print(f"[robotx] Ignoring pick/place command for unknown object: {message.data}")
            return

        if action == "attach":
            if not self.is_end_effector_near_object(object_name):
                print(f"[robotx] Refused attach for {object_name}: end-effector is not close enough")
                return
            self.attached_object_name = object_name
            print(f"[robotx] Attached {object_name} to {self.end_effector_path}")
        elif action == "detach":
            self.detach_object(object_name)
        else:
            print(f"[robotx] Ignoring unknown pick/place command: {message.data}")

    def update_attached_object(self):
        if not self.attached_object_name:
            return

        object_path = PICK_PLACE_OBJECTS[self.attached_object_name]
        object_prim = self.stage.GetPrimAtPath(object_path)
        end_effector_prim = self.stage.GetPrimAtPath(self.end_effector_path)
        if not object_prim or not end_effector_prim:
            return

        target_position = get_prim_world_center(end_effector_prim) + GRASP_OFFSET
        set_prim_translation(object_prim, target_position)

    def detach_object(self, object_name: str):
        if self.attached_object_name == object_name:
            self.update_attached_object()
            self.attached_object_name = None
        print(f"[robotx] Detached {object_name} at current end-effector pose")

    def is_end_effector_near_object(self, object_name: str) -> bool:
        object_prim = self.stage.GetPrimAtPath(PICK_PLACE_OBJECTS[object_name])
        end_effector_prim = self.stage.GetPrimAtPath(self.end_effector_path)
        if not object_prim or not end_effector_prim:
            return False

        object_position = get_prim_world_center(object_prim)
        end_effector_position = get_prim_world_center(end_effector_prim)
        distance = (object_position - end_effector_position).GetLength()
        print(
            f"[robotx] Attach distance for {object_name}: {distance:.3f} m "
            f"object=({object_position[0]:.3f}, {object_position[1]:.3f}, {object_position[2]:.3f}) "
            f"ee=({end_effector_position[0]:.3f}, {end_effector_position[1]:.3f}, {end_effector_position[2]:.3f})"
        )
        if distance > 0.15:
            self.print_closest_robot_prims(object_position)
        return distance <= 0.15

    def print_closest_robot_prims(self, object_position: Gf.Vec3d):
        candidates = []
        for prim in self.stage.Traverse():
            path = str(prim.GetPath())
            if not path.startswith(ROBOT_STAGE_PATH):
                continue
            if not prim.IsA(UsdGeom.Xformable):
                continue
            try:
                position = get_prim_world_center(prim)
            except Exception:
                continue
            distance = (object_position - position).GetLength()
            candidates.append((distance, path, position))

        for distance, path, position in sorted(candidates, key=lambda item: item[0])[:8]:
            print(
                f"[robotx] Closest robot prim: {distance:.3f} m {path} "
                f"pos=({position[0]:.3f}, {position[1]:.3f}, {position[2]:.3f})"
            )


def find_end_effector_path(stage, robot_path: str) -> str:
    candidates = []
    known_paths = (
        f"{robot_path}/tool0",
        f"{robot_path}/tcp",
        f"{robot_path}/flange",
        f"{robot_path}/wrist_3_link",
        f"{robot_path}/wrist_3",
    )
    for path in known_paths:
        if stage.GetPrimAtPath(path):
            return path

    for prim in stage.Traverse():
        path = str(prim.GetPath())
        if not path.startswith(robot_path):
            continue
        name = prim.GetName().lower()
        if any(hint in name for hint in END_EFFECTOR_NAME_HINTS):
            candidates.append(path)

    if candidates:
        candidates.sort(key=lambda item: (score_end_effector_path(item), len(item)), reverse=True)
        return candidates[0]

    robot_prim = stage.GetPrimAtPath(robot_path)
    if robot_prim:
        return str(robot_prim.GetPath())
    return robot_path


def score_end_effector_path(path: str) -> int:
    name = path.lower()
    if "tool0" in name or "tcp" in name or "ee" in name:
        return 4
    if "flange" in name:
        return 3
    if "wrist_3" in name:
        return 2
    return 1


def set_prim_translation(prim, translation: Gf.Vec3d):
    xform = UsdGeom.Xformable(prim)
    translate_op = None
    for op in xform.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            translate_op = op
            break
    if translate_op is None:
        translate_op = xform.AddTranslateOp()
    translate_op.Set(translation)


def get_prim_world_center(prim) -> Gf.Vec3d:
    try:
        bbox_cache = UsdGeom.BBoxCache(
            Usd.TimeCode.Default(),
            [UsdGeom.Tokens.default_, UsdGeom.Tokens.render, UsdGeom.Tokens.proxy],
        )
        box = bbox_cache.ComputeWorldBound(prim).ComputeAlignedBox()
        if not box.IsEmpty():
            return box.GetMidpoint()
    except Exception:
        pass
    return UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(0.0).ExtractTranslation()


asyncio.ensure_future(setup_ur3e_ros2_action_graph())
