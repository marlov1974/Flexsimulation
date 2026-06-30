from random import Random

from flexsimulation.base_load_objects import (
    AlwaysLightObject,
    ColdApplianceObject,
    InternetObject,
    SimulationContext,
    StandbyClusterObject,
    TowelRailObject,
)


def test_base_load_objects_return_non_negative_kwh() -> None:
    context = SimulationContext(timestep=1)
    rng = Random(1)
    objects = (
        ColdApplianceObject("O1", 1, "S1", "fridge", 0.1, 0.25, 4, 0),
        InternetObject("O2", 1, "S1", 0.02, 0.04),
        StandbyClusterObject("O3", 1, "S1", "site", 2, 5.0, 0.05),
        AlwaysLightObject("O4", 1, "S1", 0.75),
        TowelRailObject("O5", 1, "S1", 0.08, 0.20),
    )

    for load_object in objects:
        assert load_object.expected_kwh(context) >= 0.0
        assert load_object.actual_kwh(context, rng) >= 0.0


def test_cold_appliance_actual_varies_over_cycle() -> None:
    appliance = ColdApplianceObject("O1", 1, "S1", "freezer", 0.12, 0.25, 4, 0)
    rng = Random(1)

    values = [appliance.actual_kwh(SimulationContext(timestep=timestep), rng) for timestep in range(8)]

    assert min(values) == 0.0
    assert max(values) > 0.0


def test_stochastic_objects_can_turn_off() -> None:
    light = AlwaysLightObject("O1", 1, "S1", 0.50)
    towel_rail = TowelRailObject("O2", 1, "S1", 0.08, 0.30)
    context = SimulationContext(timestep=1)

    light_values = [light.actual_kwh(context, Random(seed)) for seed in range(20)]
    towel_rail_values = [towel_rail.actual_kwh(context, Random(seed)) for seed in range(20)]

    assert 0.0 in light_values
    assert max(light_values) > 0.0
    assert 0.0 in towel_rail_values
    assert max(towel_rail_values) > 0.0
