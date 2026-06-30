"""Latent base-load simulation objects for P0002.

These objects are synthetic reality objects. They are debug/source data for
simulation and must not be exposed through ML or bidding observations.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class SimulationContext:
    """Minimal timestep context for object-level load methods."""

    timestep: int
    step_hours: float = 0.25


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

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return max(0.0, self.rated_kw * self.duty_cycle * context.step_hours)

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return cyclic actual energy for the timestep."""

        if self.cycle_length_steps <= 0:
            return self.expected_kwh(context)
        on_steps = max(1, round(self.duty_cycle * self.cycle_length_steps))
        cycle_position = (context.timestep + self.phase_offset) % self.cycle_length_steps
        if cycle_position < on_steps:
            return max(0.0, self.rated_kw * context.step_hours)
        return 0.0


@dataclass(frozen=True)
class InternetObject:
    """Synthetic always-on network unit."""

    object_id: str
    household_id: int
    site_id: str
    kw: float
    noise_std_pct: float

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return max(0.0, self.kw * context.step_hours)

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual energy with small synthetic noise."""

        return _noisy_kwh(self.kw, self.noise_std_pct, context, rng)


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

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        kw = (self.unit_count * self.watt_per_unit) / 1000.0
        return max(0.0, kw * context.step_hours)

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return near-constant actual energy with small synthetic noise."""

        kw = (self.unit_count * self.watt_per_unit) / 1000.0
        return _noisy_kwh(kw, self.noise_std_pct, context, rng)


@dataclass(frozen=True)
class AlwaysLightObject:
    """Synthetic often-on 50 W light."""

    object_id: str
    household_id: int
    site_id: str
    on_probability_per_step: float
    kw: float = 0.05

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return max(0.0, self.kw * self.on_probability_per_step * context.step_hours)

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual energy for the timestep."""

        if rng.random() < self.on_probability_per_step:
            return max(0.0, self.kw * context.step_hours)
        return 0.0


@dataclass(frozen=True)
class TowelRailObject:
    """Synthetic stochastic towel-rail load."""

    object_id: str
    household_id: int
    site_id: str
    kw: float
    on_probability_per_step: float

    def expected_kwh(self, context: SimulationContext) -> float:
        """Return expected energy for the timestep."""

        return max(0.0, self.kw * self.on_probability_per_step * context.step_hours)

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        """Return stochastic actual energy for the timestep."""

        if rng.random() < self.on_probability_per_step:
            return max(0.0, self.kw * context.step_hours)
        return 0.0


BaseLoadObject = (
    ColdApplianceObject
    | InternetObject
    | StandbyClusterObject
    | AlwaysLightObject
    | TowelRailObject
)


def _noisy_kwh(kw: float, noise_std_pct: float, context: SimulationContext, rng: Random) -> float:
    multiplier = rng.gauss(1.0, noise_std_pct)
    return max(0.0, kw * multiplier * context.step_hours)
