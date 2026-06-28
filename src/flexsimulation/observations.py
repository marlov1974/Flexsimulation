"""Observation-layer helpers.

The observation layer is the only interface ML/bidding models should use.
"""

from __future__ import annotations

from .models import EnergyChannels, HouseholdObservation


ALLOWED_OBSERVATION_FIELDS = {
    "total_power_kw",
    "pv_power_kw",
    "ev_power_kw",
    "heatpump_power_kw",
    "battery_power_kw",
}


def create_household_observation(
    household_id: int,
    timestep: int,
    actual: EnergyChannels,
    planned: EnergyChannels,
) -> HouseholdObservation:
    """Create a household observation without latent simulator state."""

    return HouseholdObservation(
        household_id=household_id,
        timestep=timestep,
        actual=actual,
        planned=planned,
    )
