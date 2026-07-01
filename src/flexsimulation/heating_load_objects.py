"""Uncontrolled heating load objects for P0005."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from .base_load_objects import SimulationContext
from .heating_demand import HeatingDemandModel


def require_outdoor_temp_c(context: SimulationContext) -> float:
    """Return outdoor temperature or fail clearly for heating objects."""

    if context.outdoor_temp_c is None:
        raise ValueError("outdoor_temp_c is required for uncontrolled heating load objects")
    return context.outdoor_temp_c


@dataclass(frozen=True)
class DirectElectricHeatingObject:
    """Uncontrolled direct electric heating load."""

    object_id: str
    household_id: int
    site_id: str
    max_electric_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    heating_role: str = "primary"

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        return min(self.max_electric_kw, self.demand_model.thermal_need_kw(outdoor_temp_c))

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        return _noisy_kw(self.expected_kw(context), self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class GroundSourceHeatPumpLoadObject:
    """Uncontrolled ground-source heat-pump load."""

    object_id: str
    household_id: int
    site_id: str
    max_thermal_output_kw: float
    nominal_cop: float
    min_cop: float
    load_cop_penalty: float
    backup_electric_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    heating_role: str = "primary"

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        thermal_need_kw = self.demand_model.thermal_need_kw(outdoor_temp_c)
        hp_thermal_kw = min(thermal_need_kw, self.max_thermal_output_kw)
        load_fraction = hp_thermal_kw / self.max_thermal_output_kw if self.max_thermal_output_kw else 0.0
        cop = max(self.min_cop, self.nominal_cop - self.load_cop_penalty * load_fraction)
        hp_electric_kw = hp_thermal_kw / cop
        backup_kw = min(self.backup_electric_kw, max(0.0, thermal_need_kw - hp_thermal_kw))
        return max(0.0, hp_electric_kw + backup_kw)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        return _noisy_kw(self.expected_kw(context), self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class AirAirHeatPumpLoadObject:
    """Uncontrolled air-air heat-pump load."""

    object_id: str
    household_id: int
    site_id: str
    max_thermal_output_kw_at_7c: float
    backup_electric_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    cold_noise_multiplier: float
    cop_curve: dict[float, float] = field(
        default_factory=lambda: {10.0: 4.5, 0.0: 3.2, -10.0: 2.2, -20.0: 1.5}
    )
    capacity_factor_curve: dict[float, float] = field(
        default_factory=lambda: {7.0: 1.0, 0.0: 0.85, -10.0: 0.65, -20.0: 0.45}
    )
    heating_role: str = "primary"

    def cop_at_temp(self, outdoor_temp_c: float) -> float:
        return _interpolate_curve(self.cop_curve, outdoor_temp_c)

    def capacity_factor_at_temp(self, outdoor_temp_c: float) -> float:
        return _interpolate_curve(self.capacity_factor_curve, outdoor_temp_c)

    def effective_noise_std_pct(self, outdoor_temp_c: float) -> float:
        if outdoor_temp_c < 0:
            return self.noise_std_pct * self.cold_noise_multiplier
        return self.noise_std_pct

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        return _air_source_expected_kw(self, outdoor_temp_c)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        return _noisy_kw(self.expected_kw(context), self.effective_noise_std_pct(outdoor_temp_c), rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class AirWaterHeatPumpLoadObject:
    """Uncontrolled air-water heat-pump load."""

    object_id: str
    household_id: int
    site_id: str
    max_thermal_output_kw_at_7c: float
    backup_electric_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    cold_noise_multiplier: float
    cop_curve: dict[float, float] = field(
        default_factory=lambda: {10.0: 4.0, 0.0: 2.9, -10.0: 2.0, -20.0: 1.4}
    )
    capacity_factor_curve: dict[float, float] = field(
        default_factory=lambda: {7.0: 1.0, 0.0: 0.80, -10.0: 0.58, -20.0: 0.38}
    )
    heating_role: str = "primary"

    def cop_at_temp(self, outdoor_temp_c: float) -> float:
        return _interpolate_curve(self.cop_curve, outdoor_temp_c)

    def capacity_factor_at_temp(self, outdoor_temp_c: float) -> float:
        return _interpolate_curve(self.capacity_factor_curve, outdoor_temp_c)

    def effective_noise_std_pct(self, outdoor_temp_c: float) -> float:
        if outdoor_temp_c < 0:
            return self.noise_std_pct * self.cold_noise_multiplier
        return self.noise_std_pct

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        return _air_source_expected_kw(self, outdoor_temp_c)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        return _noisy_kw(self.expected_kw(context), self.effective_noise_std_pct(outdoor_temp_c), rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class ExhaustAirHeatPumpLoadObject:
    """Uncontrolled exhaust-air heat-pump load."""

    object_id: str
    household_id: int
    site_id: str
    recovery_thermal_kw: float
    cop: float
    backup_electric_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    heating_role: str = "primary"

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        thermal_need_kw = self.demand_model.thermal_need_kw(outdoor_temp_c)
        recovered_thermal_kw = min(self.recovery_thermal_kw, thermal_need_kw)
        compressor_kw = recovered_thermal_kw / self.cop
        remaining_thermal_kw = max(0.0, thermal_need_kw - recovered_thermal_kw)
        backup_kw = min(self.backup_electric_kw, remaining_thermal_kw)
        return max(0.0, compressor_kw + backup_kw)

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        return _noisy_kw(self.expected_kw(context), self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


@dataclass(frozen=True)
class PelletStoveLoadObject:
    """Uncontrolled pellet-stove auxiliary electric load."""

    object_id: str
    household_id: int
    site_id: str
    running_thermal_need_threshold_kw: float
    thermal_output_kw: float
    demand_model: HeatingDemandModel
    noise_std_pct: float
    electric_kw_when_running: float = 0.5
    heating_role: str = "primary"

    def expected_kw(self, context: SimulationContext) -> float:
        outdoor_temp_c = require_outdoor_temp_c(context)
        thermal_need_kw = self.demand_model.thermal_need_kw(outdoor_temp_c)
        if thermal_need_kw > self.running_thermal_need_threshold_kw:
            return max(0.0, self.electric_kw_when_running)
        return 0.0

    def actual_kw(self, context: SimulationContext, rng: Random) -> float:
        return _noisy_kw(self.expected_kw(context), self.noise_std_pct, rng)

    def expected_kwh(self, context: SimulationContext) -> float:
        return self.expected_kw(context) * context.step_hours

    def actual_kwh(self, context: SimulationContext, rng: Random) -> float:
        return self.actual_kw(context, rng) * context.step_hours


HeatingLoadObject = (
    DirectElectricHeatingObject
    | GroundSourceHeatPumpLoadObject
    | AirAirHeatPumpLoadObject
    | AirWaterHeatPumpLoadObject
    | ExhaustAirHeatPumpLoadObject
    | PelletStoveLoadObject
)

HEATING_LOAD_OBJECT_TYPES = (
    DirectElectricHeatingObject,
    GroundSourceHeatPumpLoadObject,
    AirAirHeatPumpLoadObject,
    AirWaterHeatPumpLoadObject,
    ExhaustAirHeatPumpLoadObject,
    PelletStoveLoadObject,
)


def _air_source_expected_kw(
    load_object: AirAirHeatPumpLoadObject | AirWaterHeatPumpLoadObject,
    outdoor_temp_c: float,
) -> float:
    thermal_need_kw = load_object.demand_model.thermal_need_kw(outdoor_temp_c)
    cop = load_object.cop_at_temp(outdoor_temp_c)
    capacity_factor = load_object.capacity_factor_at_temp(outdoor_temp_c)
    available_thermal_kw = load_object.max_thermal_output_kw_at_7c * capacity_factor
    hp_thermal_kw = min(thermal_need_kw, available_thermal_kw)
    hp_electric_kw = hp_thermal_kw / cop
    backup_kw = min(load_object.backup_electric_kw, max(0.0, thermal_need_kw - hp_thermal_kw))
    return max(0.0, hp_electric_kw + backup_kw)


def _interpolate_curve(curve: dict[float, float], x_value: float) -> float:
    points = sorted((float(x), float(y)) for x, y in curve.items())
    if not points:
        raise ValueError("curve must not be empty")
    if x_value <= points[0][0]:
        return points[0][1]
    if x_value >= points[-1][0]:
        return points[-1][1]
    for (left_x, left_y), (right_x, right_y) in zip(points, points[1:], strict=True):
        if left_x <= x_value <= right_x:
            fraction = (x_value - left_x) / (right_x - left_x)
            return left_y + fraction * (right_y - left_y)
    return points[-1][1]


def _noisy_kw(expected_kw: float, noise_std_pct: float, rng: Random) -> float:
    return max(0.0, expected_kw * rng.gauss(1.0, noise_std_pct))
