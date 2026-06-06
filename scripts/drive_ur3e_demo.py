from pathlib import Path
import asyncio
import math

import numpy as np
import omni.kit.app
import omni.timeline
import omni.usd


REPO_ROOT = Path(__file__).resolve().parents[1]
UR3E_STAGE = REPO_ROOT / "assets" / "ur3e" / "ur3e.usd"


async def drive_ur3e_demo():
    from isaacsim.core.prims import Articulation

    app = omni.kit.app.get_app()
    await app.next_update_async()
    result = await omni.usd.get_context().open_stage_async(str(UR3E_STAGE))
    print(f"[robotx] Opened UR3e stage: {UR3E_STAGE} result={result}")

    # Let payloads and UI settle before creating physics handles.
    for _ in range(20):
        await app.next_update_async()

    robot = Articulation(prim_paths_expr="/ur3e", name="ur3e", reset_xform_properties=False)
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()

    for _ in range(30):
        await app.next_update_async()

    joint_count = 6
    print("[robotx] Driving UR3e articulation with direct joint position targets")

    base = np.zeros(joint_count)
    amplitude = np.array([0.45, 0.35, 0.45, 0.30, 0.30, 0.25])
    phase = np.array([0.0, 1.1, 2.0, 2.8, 3.4, 4.2])
    t = 0.0

    while True:
        targets = base + amplitude * np.sin(t + phase)
        robot.set_joint_positions(np.array([targets]))
        await app.next_update_async()
        t += 0.035


asyncio.ensure_future(drive_ur3e_demo())
