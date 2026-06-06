from pathlib import Path
import asyncio

import omni.graph.core as og
import omni.kit.app
import omni.timeline
import omni.usd
from pxr import Sdf, UsdPhysics
import usdrt


REPO_ROOT = Path(__file__).resolve().parents[1]
UR3E_STAGE = REPO_ROOT / "assets" / "ur3e" / "ur3e.usd"
GRAPH_PATH = "/ActionGraph"
ROBOT_STAGE_PATH = "/ur3e"
COMMAND_TOPIC = "/joint_command"
STATE_TOPIC = "/joint_states"
CLOCK_TOPIC = "/clock"


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


asyncio.ensure_future(setup_ur3e_ros2_action_graph())
