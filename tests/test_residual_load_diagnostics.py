from pathlib import Path

from flexsimulation.base_load_timeseries import BaseLoadTimeSeriesConfig, simulate_base_load_timeseries
from flexsimulation.population import StockGenerationConfig
from flexsimulation.residual_load_diagnostics import (
    create_residual_load_diagnostics,
    export_diagnostics_to_csv,
)
from flexsimulation.simulation_time import create_2025_time_index
from flexsimulation.stock_generator import generate_synthetic_stock


def _small_diagnostics():
    households = generate_synthetic_stock(seed=4, config=StockGenerationConfig(households=4))
    base_load = simulate_base_load_timeseries(
        households=households,
        config=BaseLoadTimeSeriesConfig(
            simulation_seed=8,
            time_index=create_2025_time_index()[:96],
        ),
    )
    return create_residual_load_diagnostics(base_load, households), base_load


def test_portfolio_summary_contains_required_metrics() -> None:
    diagnostics, _ = _small_diagnostics()
    summary = diagnostics.portfolio_summary.iloc[0]

    assert summary["annual_actual_base_load_mwh"] > 0
    assert summary["annual_expected_base_load_mwh"] > 0
    assert summary["p01_actual_base_load_mw"] <= summary["p50_actual_base_load_mw"]
    assert summary["p99_actual_base_load_mw"] >= summary["p95_actual_base_load_mw"]
    assert summary["mean_abs_forecast_error_mw"] >= 0
    assert 0 < summary["portfolio_load_factor"] <= 1


def test_site_segment_summary_groups_without_timestep_double_counting() -> None:
    diagnostics, base_load = _small_diagnostics()
    site_count = base_load.site["site_id"].nunique()
    segment_types = set(diagnostics.site_segment_summary["segment_type"])

    assert {"site_type", "site_role", "size_class", "site_type_size_class"} <= segment_types
    assert diagnostics.site_segment_summary["site_count"].max() <= site_count
    assert (
        diagnostics.site_segment_summary.query("segment_type == 'site_type'")["site_count"].sum()
        == site_count
    )


def test_household_summary_enriches_metadata() -> None:
    diagnostics, base_load = _small_diagnostics()
    summary = diagnostics.household_summary

    assert {"all", "site_configuration", "persons_count"} <= set(summary["segment_type"])
    assert summary.query("segment_type == 'all'")["household_count"].iloc[0] == base_load.household[
        "household_id"
    ].nunique()
    assert summary["annual_actual_base_load_kwh_per_household_mean"].gt(0).all()


def test_time_shape_and_forecast_error_diagnostics() -> None:
    diagnostics, _ = _small_diagnostics()

    assert len(diagnostics.hourly_shape) == 24
    assert len(diagnostics.monthly_shape) == 1
    assert "period_actual_base_load_mwh" in diagnostics.monthly_shape.columns
    assert {"site", "household", "portfolio"} == set(diagnostics.forecast_error_summary["level"])
    assert "p95_abs_forecast_error_mw" in diagnostics.forecast_error_summary.columns
    assert "p95_abs_forecast_error_kw" in diagnostics.forecast_error_summary.columns


def test_quality_checks_pass_for_full_year_default_result() -> None:
    base_load = simulate_base_load_timeseries()
    diagnostics = create_residual_load_diagnostics(base_load)

    assert len(diagnostics.monthly_shape) == 12
    assert diagnostics.quality_checks["passed"].all()
    assert "object_id" not in diagnostics.portfolio_summary.columns
    assert "object_type" not in diagnostics.site_segment_summary.columns


def test_export_diagnostics_to_csv(tmp_path: Path) -> None:
    diagnostics, _ = _small_diagnostics()

    paths = export_diagnostics_to_csv(diagnostics, tmp_path)

    assert len(paths) == 7
    assert all(path.exists() for path in paths)
    assert {path.name for path in paths} == {
        "portfolio_summary.csv",
        "site_segment_summary.csv",
        "household_summary.csv",
        "hourly_shape.csv",
        "monthly_shape.csv",
        "forecast_error_summary.csv",
        "quality_checks.csv",
    }
