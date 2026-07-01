import pytest

from flexsimulation.base_load_timeseries import BaseLoadTimeSeriesConfig, simulate_base_load_timeseries
from flexsimulation.heating_load_factory import add_uncontrolled_heating_objects
from flexsimulation.population import StockGenerationConfig
from flexsimulation.residual_load_diagnostics import create_residual_load_diagnostics
from flexsimulation.stock_generator import generate_synthetic_stock
from flexsimulation.temperature import SyntheticTemperatureProvider


def test_heating_timeseries_requires_temperature_provider() -> None:
    households = add_uncontrolled_heating_objects(
        generate_synthetic_stock(seed=5, config=StockGenerationConfig(households=3)),
        seed=6,
    )

    with pytest.raises(ValueError, match="temperature_provider"):
        simulate_base_load_timeseries(households=households)


def test_default_full_year_heating_simulation_and_diagnostics_work() -> None:
    base_households = generate_synthetic_stock(seed=5)
    heating_households = add_uncontrolled_heating_objects(base_households, seed=6)
    base_result = simulate_base_load_timeseries(households=base_households)
    heating_result = simulate_base_load_timeseries(
        households=heating_households,
        config=BaseLoadTimeSeriesConfig(
            temperature_provider=SyntheticTemperatureProvider(),
        ),
    )
    diagnostics = create_residual_load_diagnostics(heating_result, heating_households)

    assert len(heating_result.portfolio) == 35_040
    assert (
        heating_result.portfolio["actual_base_load_mwh"].sum()
        > base_result.portfolio["actual_base_load_mwh"].sum()
    )
    assert diagnostics.quality_checks["passed"].all()
    assert "object_id" not in heating_result.site.columns
