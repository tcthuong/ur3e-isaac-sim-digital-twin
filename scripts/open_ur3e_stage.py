from pathlib import Path
import asyncio

import omni.kit.app
import omni.usd


REPO_ROOT = Path(__file__).resolve().parents[1]
UR3E_STAGE = REPO_ROOT / "assets" / "ur3e" / "ur3e.usd"


async def open_ur3e_stage():
    await omni.kit.app.get_app().next_update_async()
    result = await omni.usd.get_context().open_stage_async(str(UR3E_STAGE))
    print(f"[robotx] Opened UR3e stage: {UR3E_STAGE} result={result}")


asyncio.ensure_future(open_ur3e_stage())
