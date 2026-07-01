"""Time-index helpers for 15-minute base-load simulation."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from .base_load_objects import SimulationContext


def create_2025_time_index(step_minutes: int = 15) -> tuple[datetime, ...]:
    """Create the timezone-naive 2025 simulation time index."""

    if step_minutes <= 0:
        raise ValueError("step_minutes must be positive")

    start = datetime(2025, 1, 1, 0, 0)
    end_exclusive = datetime(2026, 1, 1, 0, 0)
    timestamps: list[datetime] = []
    current = start
    step = timedelta(minutes=step_minutes)
    while current < end_exclusive:
        timestamps.append(current)
        current += step
    return tuple(timestamps)


def create_simulation_contexts(
    timestamps: tuple[datetime, ...],
    step_minutes: int = 15,
    outdoor_temp_by_timestep: tuple[float, ...] | None = None,
) -> tuple[SimulationContext, ...]:
    """Create simulation contexts from a timestamp index."""

    if outdoor_temp_by_timestep is not None and len(outdoor_temp_by_timestep) != len(timestamps):
        raise ValueError("outdoor_temp_by_timestep must match timestamps length")

    return tuple(
        SimulationContext(
            timestep=timestep,
            timestamp=timestamp,
            step_hours=step_minutes / 60.0,
            outdoor_temp_c=outdoor_temp_by_timestep[timestep]
            if outdoor_temp_by_timestep is not None
            else None,
        )
        for timestep, timestamp in enumerate(timestamps)
    )


def stable_seed(base_seed: int, timestep: int, object_id: str) -> int:
    """Return deterministic per-object/per-timestep seed."""

    seed_input = f"{base_seed}|{timestep}|{object_id}".encode("utf-8")
    digest = hashlib.sha256(seed_input).digest()
    return int.from_bytes(digest[:8], "big", signed=False)
