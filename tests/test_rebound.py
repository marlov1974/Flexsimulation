from flexsimulation.rebound import create_rebound_position, deferred_energy_kwh


def test_deferred_energy_15_minutes() -> None:
    assert deferred_energy_kwh(11.0, 15) == 2.75


def test_create_rebound_position() -> None:
    rebound = create_rebound_position(
        rebound_id="R0001",
        household_id=1,
        asset_type="ev",
        created_timestep=36,
        power_kw=11.0,
        duration_minutes=15,
        earliest_recovery_timestep=37,
        latest_recovery_timestep=68,
        max_recovery_kw=11.0,
        source_activation_id="A0001",
    )

    assert rebound.energy_kwh == 2.75
    assert rebound.status == "open"
