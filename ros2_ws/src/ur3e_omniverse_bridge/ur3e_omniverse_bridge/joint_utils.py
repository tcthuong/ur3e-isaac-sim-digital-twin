import math
from typing import Iterable, List, Sequence, Tuple


ROS_UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

USD_SHORT_JOINT_NAMES = [
    "shoulder",
    "upper_arm",
    "elbow",
    "wrist_1",
    "wrist_2",
    "wrist_3",
]

_JOINT_NAME_MODES = {
    "ros": ROS_UR3E_JOINT_NAMES,
    "ur": ROS_UR3E_JOINT_NAMES,
    "ur3e": ROS_UR3E_JOINT_NAMES,
    "usd_short": USD_SHORT_JOINT_NAMES,
    "usd": USD_SHORT_JOINT_NAMES,
}


def parse_names(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, Iterable):
        return [str(part).strip() for part in value if str(part).strip()]
    return []


def resolve_joint_names(mode: str = "ros", custom_names: object = None) -> List[str]:
    names = parse_names(custom_names)
    if names:
        return names

    key = (mode or "ros").strip().lower()
    if key not in _JOINT_NAME_MODES:
        known = ", ".join(sorted(_JOINT_NAME_MODES))
        raise ValueError(f"Unknown joint name mode '{mode}'. Expected one of: {known}")
    return list(_JOINT_NAME_MODES[key])


def sine_positions(
    elapsed_seconds: float,
    joint_count: int,
    amplitude: float = 0.35,
    speed: float = 0.6,
) -> List[float]:
    if joint_count < 0:
        raise ValueError("joint_count must be non-negative")

    scales = [0.65, 0.5, 0.55, 0.35, 0.3, 0.25]
    elapsed = float(elapsed_seconds)
    return [
        float(amplitude) * scales[index % len(scales)] * math.sin(float(speed) * elapsed + index * 0.7)
        for index in range(joint_count)
    ]


def map_joint_positions(
    incoming_names: Sequence[str],
    incoming_positions: Sequence[float],
    source_names: object = None,
    target_names: object = None,
) -> Tuple[List[str], List[float]]:
    incoming_names = list(incoming_names)
    incoming_positions = list(incoming_positions)
    source = parse_names(source_names)
    target = parse_names(target_names)

    if len(incoming_positions) < len(incoming_names):
        raise ValueError("incoming_positions must contain at least one value per incoming name")

    if not source:
        source = incoming_names

    if target and len(target) != len(source):
        raise ValueError("target_names must have the same length as source_names")

    by_name = {
        name: float(incoming_positions[index])
        for index, name in enumerate(incoming_names)
        if index < len(incoming_positions)
    }

    missing = [name for name in source if name not in by_name]
    if missing:
        raise ValueError(f"Incoming joint state is missing joints: {', '.join(missing)}")

    output_names = target if target else list(source)
    output_positions = [by_name[name] for name in source]
    return output_names, output_positions


def duration_to_seconds(duration_msg: object) -> float:
    sec = getattr(duration_msg, "sec", 0)
    nanosec = getattr(duration_msg, "nanosec", 0)
    return float(sec) + float(nanosec) * 1e-9


def joint_payload_to_names_positions(payload: object, default_names: object = None) -> Tuple[List[str], List[float]]:
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a JSON object")

    if "name" in payload or "position" in payload:
        names = parse_names(payload.get("name", []))
        positions = payload.get("position", [])
        if not isinstance(positions, list):
            raise ValueError("'position' must be a list")
        if len(names) != len(positions):
            raise ValueError("'name' and 'position' must have the same length")
        return names, [float(value) for value in positions]

    positions_by_name = payload.get("positions")
    if isinstance(positions_by_name, dict):
        names = resolve_joint_names(custom_names=default_names)
        missing = [name for name in names if name not in positions_by_name]
        if missing:
            raise ValueError(f"'positions' is missing joints: {', '.join(missing)}")
        return names, [float(positions_by_name[name]) for name in names]

    raise ValueError("Payload must contain either 'name' with 'position', or a 'positions' object")
