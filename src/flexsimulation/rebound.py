"""Rebound accounting helpers."""

from __future__ import annotations

from .models import ReboundPosition


def deferred_energy_kwh(power_kw: float, duration_minutes: int) -> float:
    """Return deferred energy from paused or shifted power."""

    return power_kw * duration_minutes / 60.0


def create_rebound_position(
    rebound_id: str,
    household_id: int,
    asset_type: str,
    created_timestep: int,
    power_kw: float,
    duration_minutes: int,
    earliest_recovery_timestep: int,
    latest_recovery_timestep: int,
    max_recovery_kw: float,
    source_activation_id: str,
    market_area: str = "SE3",
) -> ReboundPosition:
    """Create a rebound position from deferred power."""

    return ReboundPosition(
        rebound_id=rebound_id,
        household_id=household_id,
        asset_type=asset_type,
        created_timestep=created_timestep,
        energy_kwh=deferred_energy_kwh(power_kw, duration_minutes),
        earliest_recovery_timestep=earliest_recovery_timestep,
        latest_recovery_timestep=latest_recovery_timestep,
        max_recovery_kw=max_recovery_kw,
        source_activation_id=source_activation_id,
        market_area=market_area,
    )
