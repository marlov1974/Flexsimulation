from random import Random

import pytest

from flexsimulation.base_load_objects import SimulationContext
from flexsimulation.heating_demand import HeatingDemandModel
from flexsimulation.heating_load_objects import (
    AirAirHeatPumpLoadObject,
    AirWaterHeatPumpLoadObject,
    DirectElectricHeatingObject,
    ExhaustAirHeatPumpLoadObject,
    GroundSourceHeatPumpLoadObject,
    PelletStoveLoadObject,
)


def _demand_model() -> HeatingDemandModel:
    return HeatingDemandModel(
        balance_temperature_c=15.0,
        design_temperature_c=-15.0,
        design_heat_loss_kw=12.0,
        internal_gain_kw=0.5,
    )


def _contexts() -> tuple[SimulationContext, SimulationContext]:
    return (
        SimulationContext(timestep=0, outdoor_temp_c=5.0),
        SimulationContext(timestep=1, outdoor_temp_c=-15.0),
    )


def test_heating_objects_require_outdoor_temperature() -> None:
    load_object = DirectElectricHeatingObject("H1", 1, "S1", 12.0, _demand_model(), 0.05)

    with pytest.raises(ValueError, match="outdoor_temp_c"):
        load_object.expected_kw(SimulationContext(timestep=0))


def test_all_heating_objects_follow_power_first_contract() -> None:
    warm, cold = _contexts()
    objects = (
        DirectElectricHeatingObject("H1", 1, "S1", 20.0, _demand_model(), 0.05),
        GroundSourceHeatPumpLoadObject("H2", 1, "S1", 8.0, 4.0, 2.6, 0.6, 4.0, _demand_model(), 0.04),
        AirAirHeatPumpLoadObject("H3", 1, "S1", 7.0, 5.0, _demand_model(), 0.06, 1.8),
        AirWaterHeatPumpLoadObject("H4", 1, "S1", 8.0, 5.0, _demand_model(), 0.055, 1.7),
        ExhaustAirHeatPumpLoadObject("H5", 1, "S1", 3.0, 2.6, 8.0, _demand_model(), 0.05),
        PelletStoveLoadObject("H6", 1, "S1", 1.0, 8.0, _demand_model(), 0.03),
    )

    for index, load_object in enumerate(objects):
        rng_for_kw = Random(index)
        rng_for_kwh = Random(index)
        expected_kw = load_object.expected_kw(cold)
        actual_kw = load_object.actual_kw(cold, rng_for_kw)

        assert load_object.heating_role == "primary"
        assert expected_kw >= 0.0
        assert actual_kw >= 0.0
        assert load_object.expected_kw(cold) >= load_object.expected_kw(warm)
        assert load_object.expected_kwh(cold) == expected_kw * cold.step_hours
        assert load_object.actual_kwh(cold, rng_for_kwh) == actual_kw * cold.step_hours


def test_air_source_cop_and_capacity_decrease_when_colder() -> None:
    load_object = AirAirHeatPumpLoadObject("H1", 1, "S1", 7.0, 5.0, _demand_model(), 0.06, 1.8)

    assert load_object.cop_at_temp(-15.0) < load_object.cop_at_temp(5.0)
    assert load_object.capacity_factor_at_temp(-15.0) < load_object.capacity_factor_at_temp(5.0)


def test_heat_pumps_use_backup_when_under_dimensioned() -> None:
    cold = SimulationContext(timestep=1, outdoor_temp_c=-20.0)
    demand = _demand_model()
    ground_source = GroundSourceHeatPumpLoadObject(
        "H1", 1, "S1", 2.0, 4.0, 2.6, 0.6, 4.0, demand, 0.04
    )
    air_water = AirWaterHeatPumpLoadObject("H2", 1, "S1", 2.0, 4.0, demand, 0.055, 1.7)

    assert ground_source.expected_kw(cold) > 2.0 / ground_source.min_cop
    assert air_water.expected_kw(cold) > 0.0


def test_pellet_stove_uses_half_kw_when_running() -> None:
    stove = PelletStoveLoadObject("H1", 1, "S1", 1.0, 8.0, _demand_model(), 0.03)

    assert stove.expected_kw(SimulationContext(timestep=0, outdoor_temp_c=-5.0)) == 0.5
