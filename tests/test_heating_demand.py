from flexsimulation.heating_demand import HeatingDemandModel


def test_thermal_need_is_non_negative_and_increases_when_colder() -> None:
    model = HeatingDemandModel(
        balance_temperature_c=15.0,
        design_temperature_c=-15.0,
        design_heat_loss_kw=10.0,
        internal_gain_kw=0.8,
    )

    warm_need = model.thermal_need_kw(12.0)
    cold_need = model.thermal_need_kw(-10.0)

    assert warm_need >= 0.0
    assert cold_need > warm_need
