from flexsimulation.models import EnergyChannels
from flexsimulation.observations import ALLOWED_OBSERVATION_FIELDS, create_household_observation


def test_residual_uncontrolled_kw() -> None:
    channels = EnergyChannels(
        total_power_kw=10.0,
        pv_power_kw=-3.0,
        ev_power_kw=4.0,
        heatpump_power_kw=2.0,
        battery_power_kw=-1.0,
    )

    assert channels.residual_uncontrolled_kw == 8.0


def test_observation_does_not_expose_latent_fields() -> None:
    observation = create_household_observation(
        household_id=1,
        timestep=36,
        actual=EnergyChannels(total_power_kw=1.0),
        planned=EnergyChannels(total_power_kw=2.0),
    )

    assert not hasattr(observation, "person")
    assert not hasattr(observation, "shower_object")
    assert not hasattr(observation, "travel_intent")
    assert "total_power_kw" in ALLOWED_OBSERVATION_FIELDS
