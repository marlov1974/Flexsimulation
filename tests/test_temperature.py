from datetime import datetime

from flexsimulation.temperature import SyntheticTemperatureProvider


def test_synthetic_temperature_provider_has_plausible_seasonality() -> None:
    provider = SyntheticTemperatureProvider()

    january = provider.outdoor_temp_c(datetime(2025, 1, 20, 6, 0))
    july = provider.outdoor_temp_c(datetime(2025, 7, 20, 15, 0))

    assert january < july
    assert -30.0 < january < 10.0
    assert 5.0 < july < 30.0
