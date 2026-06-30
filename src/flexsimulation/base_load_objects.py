"""Latent base-load simulation objects for P0002 and P0003.

These objects are synthetic reality objects. They are debug/source data for
simulation and must not be exposed through ML or bidding observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from random import Random


@dataclass(frozen=True)
class SimulationContext:
    """Time-aware context for object-level load methods."""

    timestep: int
    timestamp: datetime | None = None
    step_hours: float = 0.25

    @property
    def resolved_timestamp(self) -> datetime:
        """Return timestamp, defaulting to 2025 15-minute indexing."""

        if self.timestamp is not None:
            return self.timestamp
        return datetime(2025, 1, 1) + timedelta(minutes=15 * self.timestep)

    @property
    def month(self) -> int:
        """Return calendar month."""

        return self.resolved_timestamp.month

    @property
    def weekday(self) -> int:
        """Return weekday where Monday is 0."""

        return self.resolved_timestamp.weekday()

    @property
    def hour(self) -> int:
        """Return hour of day."""

        return self.resolved_timestamp.hour

    @property
    def minute(self) -> int:
        """Return minute of hour."""

        return self.resolved_timestamp.minute

    @property
    def quarter_of_day(self) -> int:
        """Return 15-minute slot number within day."""

        return self.hour * 4 + self.minute // 15


@dataclass(frozen=True)
class ColdApplianceObject:
    """Synthetic cold appliance with cyclic load."""

    object_id: str
    household_id: int
    site_id: str
    subtype: str
    rated_kw: float
    duty_cycle: float
    cycle_length_steps: int
    phase_offset: int

    def expected_kw(self, context: SimulationContext) -> float:
        """Return expected power for the timestep."""

        return max(0.0, self.rated_kw * self.duty_cycle)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        """Return cyclic actual power for the timestep."""

        if self.cycle_length_steps <= 0:
            return self.expected_kw(context)
        on_steps = max(1, round(self.duty_cycle * self.cycle_length_steps))
        cycle_position = (context.timestep + self.phase_offset) % self.cycle_length_steps
        if cycle_position < on_steps:
            return max(0.0, self.rated_kw)
        return 0.0

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return cyclic actual energy for the timestep."""

        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class InternetObject:
    """Synthetic always-on network unit."""

    object_id: str
    household_id: int
    site_id: str
    kw: float
    noise_std_pct: float

    def expected_kw(self, context: SimulationContext) -> float:
        """Return expected power for the timestep."""

        return max(0.0, self.kw)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual power with small synthetic noise."""

        return _noisy_kw(self.kw, self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual energy with small synthetic noise."""

        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class StandbyClusterObject:
    """Synthetic cluster of standby equipment."""

    object_id: str
    household_id: int
    site_id: str
    cluster_type: str
    unit_count: int
    watt_per_unit: float
    noise_std_pct: float

    def expected_kw(self, context: SimulationContext) -> float:
        """Return expected power for the timestep."""

        return max(0.0, (self.unit_count * self.watt_per_unit) / 1000.0)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual power with small synthetic noise."""

        return _noisy_kw(self.expected_kw(context), self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual energy with small synthetic noise."""

        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class AlwaysLightObject:
    """Synthetic often-on 50 W light."""

    object_id: str
    household_id: int
    site_id: str
    on_probability_per_step: float
    kw: float = 0.05

    def expected_kw(self, context: SimulationContext) -> float:
        """Return expected power for the timestep."""

        return max(0.0, self.kw * self.on_probability_per_step)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual power for the timestep."""

        if rng.random() < self.on_probability_per_step:
            return max(0.0, self.kw)
        return 0.0

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual energy for the timestep."""

        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class TowelRailObject:
    """Synthetic stochastic towel-rail load."""

    object_id: str
    household_id: int
    site_id: str
    kw: float
    on_probability_per_step: float

    def expected_kw(self, context: SimulationContext) -> float:
        """Return expected power for the timestep."""

        return max(0.0, self.kw * self.on_probability_per_step)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual power for the timestep."""

        if rng.random() < self.on_probability_per_step:
            return max(0.0, self.kw)
        return 0.0

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual energy for the timestep."""

        return self.actual_kw(context, rng) * context.step_hours


BaseLoadObject = (
    ColdApplianceObject
    | InternetObject
    | StandbyClusterObject
    | AlwaysLightObject
    | TowelRailObject
)


def _noisy_kw(kw: float, noise_std_pct: float, rng: Random) -> float:
    multiplier = rng.gauss(1.0, noise_std_pct)
    return max(0.0, kw * multiplier)
