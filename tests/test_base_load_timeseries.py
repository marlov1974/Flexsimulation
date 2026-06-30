from dataclasses import replace

import pandas as pd

from flexsimulation.base_load_objects import ColdApplianceObject, SimulationContext
from flexsimulation.base_load_timeseries import (
    BaseLoadTimeSeriesConfig,
    simulate_base_load_timeseries,
)
from flexsimulation.population import StockGenerationConfig
from flexsimulation.simulation_time import create_2025_time_index
from flexsimulation.stock_generator import generate_synthetic_stock


def test_base_load_energy_methods_are_derived_from_kw() -> None:
    context = SimulationContext(timestep=0, step_hours=0.25)
    appliance = ColdApplianceObject("O1", 1, "S1", "fridge", 0.12, 0.25, 4, 0)

    assert appliance.expected_kwh(context) == appliance.expected_kw(context) * 0.25
    assert appliance.actual_kwh(context, rng=None) == appliance.actual_kw(context, rng=None) * 0.25


def test_base_load_timeseries_row_counts_and_energy_relationships() -> None:
    households = generate_synthetic_stock(
        seed=5,
        config=StockGenerationConfig(households=2),
    )
    result = simulate_base_load_timeseries(
        households=households,
        config=BaseLoadTimeSeriesConfig(simulation_seed=9),
    )
    site_count = sum(len(household.sites) for household in households)

    assert len(result.site) == site_count * 35_040
    assert len(result.household) == len(households) * 35_040
    assert len(result.portfolio) == 35_040
    assert result.summary["site_count"] == site_count
    assert result.summary["household_count"] == 2
    assert result.summary["timestep_count"] == 35_040
    assert (
        result.site["actual_base_load_kwh"].round(10)
        == (result.site["actual_base_load_kw"] * 0.25).round(10)
    ).all()
    assert (
        result.household["actual_base_load_kwh"].round(10)
        == (result.household["actual_base_load_kw"] * 0.25).round(10)
    ).all()
    assert (
        result.portfolio["actual_base_load_mwh"].round(10)
        == (result.portfolio["actual_base_load_mw"] * 0.25).round(10)
    ).all()


def test_base_load_timeseries_is_reproducible() -> None:
    households = generate_synthetic_stock(seed=6, config=StockGenerationConfig(households=2))
    timestamps = create_2025_time_index()[:96]
    config = BaseLoadTimeSeriesConfig(simulation_seed=11, time_index=timestamps)

    first = simulate_base_load_timeseries(households=households, config=config)
    second = simulate_base_load_timeseries(households=households, config=config)

    pd.testing.assert_frame_equal(first.site, second.site)
    pd.testing.assert_frame_equal(first.household, second.household)
    pd.testing.assert_frame_equal(first.portfolio, second.portfolio)


def test_portfolio_totals_do_not_depend_on_object_iteration_order() -> None:
    households = generate_synthetic_stock(seed=7, config=StockGenerationConfig(households=2))
    reversed_households = tuple(
        replace(
            household,
            sites=tuple(
                replace(site, load_objects=tuple(reversed(site.load_objects)))
                for site in household.sites
            ),
        )
        for household in households
    )
    config = BaseLoadTimeSeriesConfig(
        simulation_seed=12,
        time_index=create_2025_time_index()[:96],
    )

    normal = simulate_base_load_timeseries(households=households, config=config)
    reversed_result = simulate_base_load_timeseries(households=reversed_households, config=config)

    pd.testing.assert_frame_equal(normal.portfolio, reversed_result.portfolio)


def test_normal_outputs_do_not_include_object_level_details() -> None:
    result = simulate_base_load_timeseries(
        config=BaseLoadTimeSeriesConfig(
            stock_config=StockGenerationConfig(households=1),
            time_index=create_2025_time_index()[:4],
        )
    )

    assert result.object_level is None
    for frame in (result.site, result.household, result.portfolio):
        assert "object_id" not in frame.columns
        assert "object_type" not in frame.columns
