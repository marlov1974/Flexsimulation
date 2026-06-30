"""Residual-load diagnostics for P0004."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from .base_load_timeseries import BaseLoadTimeSeriesResult
from .population import Household


@dataclass(frozen=True)
class ResidualLoadDiagnosticsResult:
    """Tabular residual-load diagnostics."""

    portfolio_summary: pd.DataFrame
    site_segment_summary: pd.DataFrame
    household_summary: pd.DataFrame
    hourly_shape: pd.DataFrame
    monthly_shape: pd.DataFrame
    forecast_error_summary: pd.DataFrame
    quality_checks: pd.DataFrame


def create_residual_load_diagnostics(
    result: BaseLoadTimeSeriesResult,
    households: tuple[Household, ...] | None = None,
) -> ResidualLoadDiagnosticsResult:
    """Create residual-load diagnostics from a P0003 base-load result."""

    site = _enrich_site_metadata(result.site.copy(), households)
    household = _enrich_household_metadata(result.household.copy(), households)
    portfolio = result.portfolio.copy()

    diagnostics = ResidualLoadDiagnosticsResult(
        portfolio_summary=create_portfolio_summary(portfolio),
        site_segment_summary=create_site_segment_summary(site),
        household_summary=create_household_summary(household),
        hourly_shape=create_hourly_shape(portfolio),
        monthly_shape=create_monthly_shape(portfolio),
        forecast_error_summary=create_forecast_error_summary(site, household, portfolio),
        quality_checks=create_quality_checks(site, household, portfolio),
    )
    return diagnostics


def create_portfolio_summary(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Create portfolio-level residual-load diagnostics."""

    actual = portfolio["actual_base_load_mw"]
    expected = portfolio["expected_base_load_mw"]
    error = portfolio["forecast_error_mw"]
    abs_error = error.abs()
    max_actual = float(actual.max())

    return pd.DataFrame(
        [
            {
                "timestep_count": len(portfolio),
                "annual_actual_base_load_mwh": float(portfolio["actual_base_load_mwh"].sum()),
                "annual_expected_base_load_mwh": float(
                    portfolio["expected_base_load_mwh"].sum()
                ),
                "mean_actual_base_load_mw": float(actual.mean()),
                "mean_expected_base_load_mw": float(expected.mean()),
                "min_actual_base_load_mw": float(actual.min()),
                "max_actual_base_load_mw": max_actual,
                "p01_actual_base_load_mw": float(actual.quantile(0.01)),
                "p05_actual_base_load_mw": float(actual.quantile(0.05)),
                "p50_actual_base_load_mw": float(actual.quantile(0.50)),
                "p95_actual_base_load_mw": float(actual.quantile(0.95)),
                "p99_actual_base_load_mw": float(actual.quantile(0.99)),
                "std_actual_base_load_mw": float(actual.std(ddof=0)),
                "mean_forecast_error_mw": float(error.mean()),
                "std_forecast_error_mw": float(error.std(ddof=0)),
                "mean_abs_forecast_error_mw": float(abs_error.mean()),
                "p95_abs_forecast_error_mw": float(abs_error.quantile(0.95)),
                "portfolio_load_factor": float(actual.mean() / max_actual)
                if max_actual > 0
                else 0.0,
            }
        ]
    )


def create_site_segment_summary(site: pd.DataFrame) -> pd.DataFrame:
    """Create site segment diagnostics without timestep double-counting."""

    rows: list[dict[str, object]] = []
    groupings = [
        ("site_type", ["site_type"]),
        ("site_role", ["site_role"]),
        ("size_class", ["site_type", "site_id"]),
    ]
    if "size_class" in site.columns:
        groupings[2] = ("size_class", ["size_class"])
        groupings.append(("site_type_size_class", ["site_type", "size_class"]))

    for segment_type, columns in groupings:
        for keys, segment in site.groupby(columns, sort=True):
            key_values = _as_tuple(keys)
            rows.append(_site_segment_row(segment_type, columns, key_values, segment))

    return pd.DataFrame(rows)


def create_household_summary(household: pd.DataFrame) -> pd.DataFrame:
    """Create household diagnostics, including metadata groupings when available."""

    rows = [_household_summary_row("all", (), (), household)]

    if "site_configuration" in household.columns:
        for keys, segment in household.groupby(["site_configuration"], sort=True):
            rows.append(_household_summary_row("site_configuration", ("site_configuration",), keys, segment))

    if "persons_count" in household.columns:
        for keys, segment in household.groupby(["persons_count"], sort=True):
            rows.append(_household_summary_row("persons_count", ("persons_count",), keys, segment))

    return pd.DataFrame(rows)


def create_hourly_shape(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Create portfolio hourly shape diagnostics."""

    shaped = portfolio.copy()
    shaped["hour"] = pd.to_datetime(shaped["timestamp"]).dt.hour
    return (
        shaped.groupby("hour", sort=True)
        .apply(_shape_row, include_groups=False)
        .reset_index()
    )


def create_monthly_shape(portfolio: pd.DataFrame) -> pd.DataFrame:
    """Create portfolio monthly shape diagnostics."""

    shaped = portfolio.copy()
    shaped["month"] = pd.to_datetime(shaped["timestamp"]).dt.month
    rows = []
    for month, segment in shaped.groupby("month", sort=True):
        row = _shape_row(segment)
        row["month"] = month
        row["period_actual_base_load_mwh"] = float(segment["actual_base_load_mwh"].sum())
        rows.append(row)
    return pd.DataFrame(rows)[
        [
            "month",
            "period_actual_base_load_mwh",
            "mean_actual_base_load_mw",
            "p05_actual_base_load_mw",
            "p50_actual_base_load_mw",
            "p95_actual_base_load_mw",
            "mean_forecast_error_mw",
            "mean_abs_forecast_error_mw",
        ]
    ]


def create_forecast_error_summary(
    site: pd.DataFrame,
    household: pd.DataFrame,
    portfolio: pd.DataFrame,
) -> pd.DataFrame:
    """Create forecast-error diagnostics for site, household and portfolio levels."""

    return pd.DataFrame(
        [
            _forecast_error_row("site", site["forecast_error_kw"], "kw"),
            _forecast_error_row("household", household["forecast_error_kw"], "kw"),
            _forecast_error_row("portfolio", portfolio["forecast_error_mw"], "mw"),
        ]
    )


def create_quality_checks(
    site: pd.DataFrame,
    household: pd.DataFrame,
    portfolio: pd.DataFrame,
    tolerance: float = 1e-9,
) -> pd.DataFrame:
    """Run basic consistency checks for residual-load diagnostics."""

    checks = [
        _check(
            "portfolio_timestep_count_is_35040",
            len(portfolio) == 35_040,
            f"portfolio rows={len(portfolio)}",
        ),
        _check(
            "portfolio_has_no_negative_actual_load",
            bool((portfolio["actual_base_load_mw"] >= 0).all()),
            "actual_base_load_mw >= 0",
        ),
        _check(
            "portfolio_has_no_negative_expected_load",
            bool((portfolio["expected_base_load_mw"] >= 0).all()),
            "expected_base_load_mw >= 0",
        ),
        _check(
            "forecast_error_equals_actual_minus_expected",
            _series_close(
                portfolio["forecast_error_mw"],
                portfolio["actual_base_load_mw"] - portfolio["expected_base_load_mw"],
                tolerance,
            ),
            "portfolio forecast_error_mw = actual - expected",
        ),
        _check(
            "portfolio_mwh_equals_mw_times_0_25",
            _series_close(
                portfolio["actual_base_load_mwh"],
                portfolio["actual_base_load_mw"] * 0.25,
                tolerance,
            ),
            "actual_base_load_mwh = actual_base_load_mw * 0.25",
        ),
        _check(
            "site_kwh_equals_kw_times_0_25",
            _series_close(
                site["actual_base_load_kwh"],
                site["actual_base_load_kw"] * 0.25,
                tolerance,
            ),
            "site actual_base_load_kwh = actual_base_load_kw * 0.25",
        ),
        _check(
            "household_kwh_equals_kw_times_0_25",
            _series_close(
                household["actual_base_load_kwh"],
                household["actual_base_load_kw"] * 0.25,
                tolerance,
            ),
            "household actual_base_load_kwh = actual_base_load_kw * 0.25",
        ),
        _check(
            "site_to_portfolio_energy_reconciles",
            abs(site["actual_base_load_kwh"].sum() / 1000.0 - portfolio["actual_base_load_mwh"].sum())
            <= tolerance,
            "sum site actual kWh / 1000 equals portfolio actual MWh",
        ),
        _check(
            "household_to_portfolio_energy_reconciles",
            abs(
                household["actual_base_load_kwh"].sum() / 1000.0
                - portfolio["actual_base_load_mwh"].sum()
            )
            <= tolerance,
            "sum household actual kWh / 1000 equals portfolio actual MWh",
        ),
    ]
    return pd.DataFrame(checks)


def export_diagnostics_to_csv(
    result: ResidualLoadDiagnosticsResult,
    output_dir: Path | str,
) -> list[Path]:
    """Write diagnostics tables to CSV files and return created paths."""

    resolved_output_dir = Path(output_dir)
    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "portfolio_summary": result.portfolio_summary,
        "site_segment_summary": result.site_segment_summary,
        "household_summary": result.household_summary,
        "hourly_shape": result.hourly_shape,
        "monthly_shape": result.monthly_shape,
        "forecast_error_summary": result.forecast_error_summary,
        "quality_checks": result.quality_checks,
    }

    paths: list[Path] = []
    for name, table in tables.items():
        path = resolved_output_dir / f"{name}.csv"
        table.to_csv(path, index=False)
        paths.append(path)
    return paths


def _site_segment_row(
    segment_type: str,
    columns: list[str],
    key_values: tuple[object, ...],
    segment: pd.DataFrame,
) -> dict[str, object]:
    annual_by_site = (
        segment.groupby("site_id", sort=True)
        .agg(
            annual_actual_base_load_kwh=("actual_base_load_kwh", "sum"),
            annual_expected_base_load_kwh=("expected_base_load_kwh", "sum"),
        )
        .reset_index()
    )
    actual = segment["actual_base_load_kw"]
    abs_error = segment["forecast_error_kw"].abs()
    row: dict[str, object] = {
        "segment_type": segment_type,
        "segment_value": "|".join(str(value) for value in key_values),
        "site_count": int(segment["site_id"].nunique()),
        "annual_actual_base_load_kwh_total": float(
            annual_by_site["annual_actual_base_load_kwh"].sum()
        ),
        "annual_expected_base_load_kwh_total": float(
            annual_by_site["annual_expected_base_load_kwh"].sum()
        ),
        "annual_actual_base_load_kwh_per_site_mean": float(
            annual_by_site["annual_actual_base_load_kwh"].mean()
        ),
        "annual_actual_base_load_kwh_per_site_p50": float(
            annual_by_site["annual_actual_base_load_kwh"].quantile(0.50)
        ),
        "mean_actual_base_load_kw_per_site": float(actual.mean()),
        "p05_actual_base_load_kw_per_site": float(actual.quantile(0.05)),
        "p50_actual_base_load_kw_per_site": float(actual.quantile(0.50)),
        "p95_actual_base_load_kw_per_site": float(actual.quantile(0.95)),
        "std_actual_base_load_kw_per_site": float(actual.std(ddof=0)),
        "mean_abs_forecast_error_kw_per_site": float(abs_error.mean()),
    }
    row.update(dict(zip(columns, key_values, strict=True)))
    return row


def _household_summary_row(
    segment_type: str,
    columns: tuple[str, ...],
    key_values: object,
    segment: pd.DataFrame,
) -> dict[str, object]:
    key_tuple = _as_tuple(key_values)
    annual_by_household = (
        segment.groupby("household_id", sort=True)
        .agg(annual_actual_base_load_kwh=("actual_base_load_kwh", "sum"))
        .reset_index()
    )
    actual = segment["actual_base_load_kw"]
    abs_error = segment["forecast_error_kw"].abs()
    row: dict[str, object] = {
        "segment_type": segment_type,
        "segment_value": "all" if not key_tuple else "|".join(str(value) for value in key_tuple),
        "household_count": int(segment["household_id"].nunique()),
        "annual_actual_base_load_kwh_per_household_mean": float(
            annual_by_household["annual_actual_base_load_kwh"].mean()
        ),
        "annual_actual_base_load_kwh_per_household_p05": float(
            annual_by_household["annual_actual_base_load_kwh"].quantile(0.05)
        ),
        "annual_actual_base_load_kwh_per_household_p50": float(
            annual_by_household["annual_actual_base_load_kwh"].quantile(0.50)
        ),
        "annual_actual_base_load_kwh_per_household_p95": float(
            annual_by_household["annual_actual_base_load_kwh"].quantile(0.95)
        ),
        "mean_actual_base_load_kw_per_household": float(actual.mean()),
        "p95_actual_base_load_kw_per_household": float(actual.quantile(0.95)),
        "mean_abs_forecast_error_kw_per_household": float(abs_error.mean()),
    }
    row.update(dict(zip(columns, key_tuple, strict=True)))
    return row


def _shape_row(segment: pd.DataFrame) -> pd.Series:
    actual = segment["actual_base_load_mw"]
    error = segment["forecast_error_mw"]
    return pd.Series(
        {
            "mean_actual_base_load_mw": float(actual.mean()),
            "p05_actual_base_load_mw": float(actual.quantile(0.05)),
            "p50_actual_base_load_mw": float(actual.quantile(0.50)),
            "p95_actual_base_load_mw": float(actual.quantile(0.95)),
            "mean_forecast_error_mw": float(error.mean()),
            "mean_abs_forecast_error_mw": float(error.abs().mean()),
        }
    )


def _forecast_error_row(level: str, error: pd.Series, unit: str) -> dict[str, object]:
    abs_error = error.abs()
    return {
        "level": level,
        f"mean_forecast_error_{unit}": float(error.mean()),
        f"mean_abs_forecast_error_{unit}": float(abs_error.mean()),
        f"std_forecast_error_{unit}": float(error.std(ddof=0)),
        f"p05_forecast_error_{unit}": float(error.quantile(0.05)),
        f"p50_forecast_error_{unit}": float(error.quantile(0.50)),
        f"p95_forecast_error_{unit}": float(error.quantile(0.95)),
        f"p95_abs_forecast_error_{unit}": float(abs_error.quantile(0.95)),
    }


def _enrich_household_metadata(
    household: pd.DataFrame,
    households: tuple[Household, ...] | None,
) -> pd.DataFrame:
    if households is None:
        return household
    metadata = pd.DataFrame(
        [
            {
                "household_id": source.household_id,
                "site_configuration": source.site_configuration,
                "persons_count": source.persons_count,
            }
            for source in households
        ]
    )
    return household.merge(metadata, on="household_id", how="left")


def _enrich_site_metadata(
    site: pd.DataFrame,
    households: tuple[Household, ...] | None,
) -> pd.DataFrame:
    if households is None:
        return site
    metadata = pd.DataFrame(
        [
            {
                "site_id": source_site.site_id,
                "size_class": source_site.size_class,
            }
            for household in households
            for source_site in household.sites
        ]
    )
    return site.merge(metadata, on="site_id", how="left")


def _check(check_name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"check_name": check_name, "passed": bool(passed), "detail": detail}


def _series_close(left: pd.Series, right: pd.Series, tolerance: float) -> bool:
    return bool(((left - right).abs() <= tolerance).all())


def _as_tuple(value: object) -> tuple[object, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, Iterable) and not isinstance(value, str):
        return tuple(value)
    return (value,)
