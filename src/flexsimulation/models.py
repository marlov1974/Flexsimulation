"""Core dataclasses for Flexsimulation.

The first package defines stable names and simple accounting helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(str, Enum):
    """Activation direction."""

    UP = "up"
    DOWN = "down"


@dataclass(frozen=True)
class EnergyChannels:
    """Observed or planned household energy channels.

    Sign convention:
    + consumption/load
    - generation/export/discharge
    """

    total_power_kw: float = 0.0
    pv_power_kw: float = 0.0
    ev_power_kw: float = 0.0
    heatpump_power_kw: float = 0.0
    battery_power_kw: float = 0.0

    @property
    def residual_uncontrolled_kw(self) -> float:
        """Return observed residual not allocated to controllable channels."""

        return (
            self.total_power_kw
            - self.pv_power_kw
            - self.ev_power_kw
            - self.heatpump_power_kw
            - self.battery_power_kw
        )


@dataclass(frozen=True)
class HouseholdObservation:
    """ML/bidding-visible household observation.

    This object must not expose latent person, behaviour or true-future simulator state.
    """

    household_id: int
    timestep: int
    actual: EnergyChannels
    planned: EnergyChannels


@dataclass(frozen=True)
class ActivationEvent:
    """Synthetic activation event."""

    activation_id: str
    start_timestep: int
    duration_steps: int
    direction: Direction
    requested_mw: float


@dataclass(frozen=True)
class ResponseAccounting:
    """Baseline-vs-actual response accounting."""

    baseline_power_kw: float
    actual_power_kw: float

    @property
    def response_kw(self) -> float:
        """Positive response means baseline consumption exceeded actual consumption."""

        return self.baseline_power_kw - self.actual_power_kw


@dataclass(frozen=True)
class ReboundPosition:
    """Deferred or advanced energy position created by activation."""

    rebound_id: str
    household_id: int
    asset_type: str
    created_timestep: int
    energy_kwh: float
    earliest_recovery_timestep: int
    latest_recovery_timestep: int
    max_recovery_kw: float
    source_activation_id: str
    market_area: str = "SE3"
    status: str = "open"
