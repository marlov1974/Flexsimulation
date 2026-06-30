"""Base-load time-series simulator for P0003."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from random import Random

import numpy as np
import pandas as pd

from .base_load_objects import (
    AlwaysLightObject,
    BaseLoadObject,
    ColdApplianceObject,
    InternetObject,
    SimulationContext,
    StandbyClusterObject,
    TowelRailObject,
)
from .population import Household, StockGenerationConfig
from .simulation_time import create_2025_time_index, create_simulation_contexts, stable_seed
from .stock_generator import generate_synthetic_stock


@dataclass(frozen=True)
class BaseLoadTimeSeriesConfig:
    """Configuration for base-load time-series simulation."""

    stock_seed: int = 1
    simulation_seed: int = 1
    step_minutes: int = 15
    time_index: tuple[datetime, ...] | None = None
    stock_config: StockGenerationConfig | None = None
    save_object_level: bool = False


@dataclass(frozen=True)
class BaseLoadTimeSeriesResult:
    """Aggregated base-load simulation outputs."""

    site: pd.DataFrame
    household: pd.DataFrame
    portfolio: pd.DataFrame
    summary: dict[str, float | int]
    object_level: pd.DataFrame | None = None


def simulate_base_load_timeseries(
    households: tuple[Household, ...] | None = None,
    config: BaseLoadTimeSeriesConfig | None = None,
) -> BaseLoadTimeSeriesResult:
    """Run base-load objects and return aggregate time series."""

    resolved_config = config or BaseLoadTimeSeriesConfig()
    resolved_households = households or generate_synthetic_stock(
        seed=resolved_config.stock_seed,
        config=resolved_config.stock_config,
    )
    timestamps = resolved_config.time_index or create_2025_time_index(
        step_minutes=resolved_config.step_minutes
    )
    sites = tuple(site for household in resolved_households for site in household.sites)

    if not resolved_config.save_object_level:
        site = _simulate_site_frames(
            sites=sites,
            timestamps=timestamps,
            step_hours=resolved_config.step_minutes / 60.0,
            simulation_seed=resolved_config.simulation_seed,
        )
        household = _aggregate_household(site)
        portfolio = _aggregate_portfolio(site)
        return BaseLoadTimeSeriesResult(
            site=site,
            household=household,
            portfolio=portfolio,
            summary=summarize_base_load_result(
                portfolio=portfolio,
                site_count=len(sites),
                household_count=len(resolved_households),
            ),
            object_level=None,
        )

    contexts = create_simulation_contexts(timestamps, step_minutes=resolved_config.step_minutes)

    site_rows: list[dict[str, object]] = []
    household_rows: list[dict[str, object]] = []
    portfolio_rows: list[dict[str, object]] = []
    object_rows: list[dict[str, object]] = []

    for context in contexts:
        household_totals = {
            household.household_id: [0.0, 0.0] for household in resolved_households
        }
        portfolio_expected_kw = 0.0
        portfolio_actual_kw = 0.0

        for site in sites:
            expected_kw, actual_kw = _tick_site(
                site.load_objects,
                context,
                resolved_config.simulation_seed,
                object_rows if resolved_config.save_object_level else None,
            )
            forecast_error_kw = actual_kw - expected_kw
            expected_kwh = expected_kw * context.step_hours
            actual_kwh = actual_kw * context.step_hours
            forecast_error_kwh = forecast_error_kw * context.step_hours

            site_rows.append(
                {
                    "timestamp": context.resolved_timestamp,
                    "timestep": context.timestep,
                    "household_id": site.household_id,
                    "site_id": site.site_id,
                    "site_type": site.site_type,
                    "site_role": site.site_role,
                    "expected_base_load_kw": expected_kw,
                    "actual_base_load_kw": actual_kw,
                    "forecast_error_kw": forecast_error_kw,
                    "expected_base_load_kwh": expected_kwh,
                    "actual_base_load_kwh": actual_kwh,
                    "forecast_error_kwh": forecast_error_kwh,
                }
            )
            household_totals[site.household_id][0] += expected_kw
            household_totals[site.household_id][1] += actual_kw
            portfolio_expected_kw += expected_kw
            portfolio_actual_kw += actual_kw

        for household_id in sorted(household_totals):
            expected_kw, actual_kw = household_totals[household_id]
            forecast_error_kw = actual_kw - expected_kw
            household_rows.append(
                {
                    "timestamp": context.resolved_timestamp,
                    "timestep": context.timestep,
                    "household_id": household_id,
                    "expected_base_load_kw": expected_kw,
                    "actual_base_load_kw": actual_kw,
                    "forecast_error_kw": forecast_error_kw,
                    "expected_base_load_kwh": expected_kw * context.step_hours,
                    "actual_base_load_kwh": actual_kw * context.step_hours,
                    "forecast_error_kwh": forecast_error_kw * context.step_hours,
                }
            )

        expected_mw = portfolio_expected_kw / 1000.0
        actual_mw = portfolio_actual_kw / 1000.0
        forecast_error_mw = actual_mw - expected_mw
        portfolio_rows.append(
            {
                "timestamp": context.resolved_timestamp,
                "timestep": context.timestep,
                "expected_base_load_mw": expected_mw,
                "actual_base_load_mw": actual_mw,
                "forecast_error_mw": forecast_error_mw,
                "expected_base_load_mwh": expected_mw * context.step_hours,
                "actual_base_load_mwh": actual_mw * context.step_hours,
                "forecast_error_mwh": forecast_error_mw * context.step_hours,
            }
        )

    site = pd.DataFrame(site_rows)
    household = pd.DataFrame(household_rows)
    portfolio = pd.DataFrame(portfolio_rows)
    object_level = pd.DataFrame(object_rows) if resolved_config.save_object_level else None
    summary = summarize_base_load_result(
        portfolio=portfolio,
        site_count=len(sites),
        household_count=len(resolved_households),
    )

    return BaseLoadTimeSeriesResult(
        site=site,
        household=household,
        portfolio=portfolio,
        summary=summary,
        object_level=object_level,
    )


def _simulate_site_frames(
    sites: tuple[object, ...],
    timestamps: tuple[datetime, ...],
    step_hours: float,
    simulation_seed: int,
) -> pd.DataFrame:
    timestep = np.arange(len(timestamps), dtype=np.int64)
    frames: list[pd.DataFrame] = []

    for site in sites:
        expected_kw, actual_kw = _site_power_arrays(
            site.load_objects,
            timestep,
            simulation_seed,
        )
        forecast_error_kw = actual_kw - expected_kw
        frames.append(
            pd.DataFrame(
                {
                    "timestamp": timestamps,
                    "timestep": timestep,
                    "household_id": site.household_id,
                    "site_id": site.site_id,
                    "site_type": site.site_type,
                    "site_role": site.site_role,
                    "expected_base_load_kw": expected_kw,
                    "actual_base_load_kw": actual_kw,
                    "forecast_error_kw": forecast_error_kw,
                    "expected_base_load_kwh": expected_kw * step_hours,
                    "actual_base_load_kwh": actual_kw * step_hours,
                    "forecast_error_kwh": forecast_error_kw * step_hours,
                }
            )
        )

    if not frames:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "timestep",
                "household_id",
                "site_id",
                "site_type",
                "site_role",
                "expected_base_load_kw",
                "actual_base_load_kw",
                "forecast_error_kw",
                "expected_base_load_kwh",
                "actual_base_load_kwh",
                "forecast_error_kwh",
            ]
        )
    return pd.concat(frames, ignore_index=True)


def _site_power_arrays(
    load_objects: tuple[BaseLoadObject, ...],
    timestep: np.ndarray,
    simulation_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    expected_kw = np.zeros(len(timestep), dtype=float)
    actual_kw = np.zeros(len(timestep), dtype=float)

    for load_object in load_objects:
        object_expected_kw, object_actual_kw = _object_power_arrays(
            load_object,
            timestep,
            simulation_seed,
        )
        expected_kw += object_expected_kw
        actual_kw += object_actual_kw

    return expected_kw, actual_kw


def _object_power_arrays(
    load_object: BaseLoadObject,
    timestep: np.ndarray,
    simulation_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    object_seed = stable_seed(simulation_seed, 0, load_object.object_id)

    if isinstance(load_object, ColdApplianceObject):
        expected_kw = np.full(len(timestep), max(0.0, load_object.rated_kw * load_object.duty_cycle))
        if load_object.cycle_length_steps <= 0:
            return expected_kw, expected_kw.copy()
        on_steps = max(1, round(load_object.duty_cycle * load_object.cycle_length_steps))
        cycle_position = (timestep + load_object.phase_offset) % load_object.cycle_length_steps
        actual_kw = np.where(cycle_position < on_steps, max(0.0, load_object.rated_kw), 0.0)
        return expected_kw, actual_kw

    if isinstance(load_object, InternetObject):
        return _near_constant_arrays(load_object.kw, load_object.noise_std_pct, timestep, object_seed)

    if isinstance(load_object, StandbyClusterObject):
        kw = (load_object.unit_count * load_object.watt_per_unit) / 1000.0
        return _near_constant_arrays(kw, load_object.noise_std_pct, timestep, object_seed)

    if isinstance(load_object, AlwaysLightObject):
        expected_kw = np.full(
            len(timestep),
            max(0.0, load_object.kw * load_object.on_probability_per_step),
        )
        actual_kw = np.where(
            _uniform_values(object_seed, timestep) < load_object.on_probability_per_step,
            max(0.0, load_object.kw),
            0.0,
        )
        return expected_kw, actual_kw

    if isinstance(load_object, TowelRailObject):
        expected_kw = np.full(
            len(timestep),
            max(0.0, load_object.kw * load_object.on_probability_per_step),
        )
        actual_kw = np.where(
            _uniform_values(object_seed, timestep) < load_object.on_probability_per_step,
            max(0.0, load_object.kw),
            0.0,
        )
        return expected_kw, actual_kw

    raise TypeError(f"unsupported base-load object type: {type(load_object).__name__}")


def _near_constant_arrays(
    kw: float,
    noise_std_pct: float,
    timestep: np.ndarray,
    object_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    expected_kw = np.full(len(timestep), max(0.0, kw))
    actual_kw = np.maximum(0.0, kw * _normal_multipliers(object_seed, timestep, noise_std_pct))
    return expected_kw, actual_kw


def _normal_multipliers(
    object_seed: int,
    timestep: np.ndarray,
    noise_std_pct: float,
) -> np.ndarray:
    u1 = np.maximum(_uniform_values(object_seed, timestep, salt=1), np.finfo(float).tiny)
    u2 = _uniform_values(object_seed, timestep, salt=2)
    standard_normal = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
    return 1.0 + noise_std_pct * standard_normal


def _uniform_values(
    object_seed: int,
    timestep: np.ndarray,
    salt: int = 0,
) -> np.ndarray:
    salt_offset = (salt * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    values = timestep.astype(np.uint64, copy=False)
    values = values + np.uint64(object_seed) + np.uint64(salt_offset)
    values = _splitmix64(values)
    return ((values >> np.uint64(11)).astype(np.float64)) / float(1 << 53)


def _splitmix64(values: np.ndarray) -> np.ndarray:
    values = values + np.uint64(0x9E3779B97F4A7C15)
    values = (values ^ (values >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    values = (values ^ (values >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return values ^ (values >> np.uint64(31))


def _aggregate_household(site: pd.DataFrame) -> pd.DataFrame:
    household = (
        site.groupby(["timestamp", "timestep", "household_id"], sort=False)[
            [
                "expected_base_load_kw",
                "actual_base_load_kw",
                "forecast_error_kw",
                "expected_base_load_kwh",
                "actual_base_load_kwh",
                "forecast_error_kwh",
            ]
        ]
        .sum()
        .reset_index()
    )
    return household


def _aggregate_portfolio(site: pd.DataFrame) -> pd.DataFrame:
    portfolio_kw = (
        site.groupby(["timestamp", "timestep"], sort=False)[
            [
                "expected_base_load_kw",
                "actual_base_load_kw",
                "forecast_error_kw",
                "expected_base_load_kwh",
                "actual_base_load_kwh",
                "forecast_error_kwh",
            ]
        ]
        .sum()
        .reset_index()
    )
    return pd.DataFrame(
        {
            "timestamp": portfolio_kw["timestamp"],
            "timestep": portfolio_kw["timestep"],
            "expected_base_load_mw": portfolio_kw["expected_base_load_kw"] / 1000.0,
            "actual_base_load_mw": portfolio_kw["actual_base_load_kw"] / 1000.0,
            "forecast_error_mw": portfolio_kw["forecast_error_kw"] / 1000.0,
            "expected_base_load_mwh": portfolio_kw["expected_base_load_kwh"] / 1000.0,
            "actual_base_load_mwh": portfolio_kw["actual_base_load_kwh"] / 1000.0,
            "forecast_error_mwh": portfolio_kw["forecast_error_kwh"] / 1000.0,
        }
    )


def summarize_base_load_result(
    portfolio: pd.DataFrame,
    site_count: int,
    household_count: int,
) -> dict[str, float | int]:
    """Return portfolio-level base-load summary metrics."""

    actual_kw = portfolio["actual_base_load_mw"] * 1000.0
    expected_kw = portfolio["expected_base_load_mw"] * 1000.0
    forecast_error_kw = portfolio["forecast_error_mw"] * 1000.0

    return {
        "site_count": site_count,
        "household_count": household_count,
        "timestep_count": len(portfolio),
        "annual_actual_base_load_kwh": float(portfolio["actual_base_load_mwh"].sum() * 1000.0),
        "annual_expected_base_load_kwh": float(
            portfolio["expected_base_load_mwh"].sum() * 1000.0
        ),
        "mean_actual_base_load_kw": float(actual_kw.mean()),
        "mean_expected_base_load_kw": float(expected_kw.mean()),
        "std_actual_base_load_kw": float(actual_kw.std(ddof=0)),
        "p05_actual_base_load_kw": float(actual_kw.quantile(0.05)),
        "p50_actual_base_load_kw": float(actual_kw.quantile(0.50)),
        "p95_actual_base_load_kw": float(actual_kw.quantile(0.95)),
        "mean_forecast_error_kw": float(forecast_error_kw.mean()),
        "std_forecast_error_kw": float(forecast_error_kw.std(ddof=0)),
    }


def _tick_site(
    load_objects: tuple[BaseLoadObject, ...],
    context: SimulationContext,
    simulation_seed: int,
    object_rows: list[dict[str, object]] | None,
) -> tuple[float, float]:
    expected_kw = 0.0
    actual_kw = 0.0

    for load_object in load_objects:
        object_expected_kw = load_object.expected_kw(context)
        rng = Random(stable_seed(simulation_seed, context.timestep, load_object.object_id))
        object_actual_kw = load_object.actual_kw(context, rng)
        expected_kw += object_expected_kw
        actual_kw += object_actual_kw

        if object_rows is not None:
            object_rows.append(
                {
                    "timestamp": context.resolved_timestamp,
                    "timestep": context.timestep,
                    "household_id": load_object.household_id,
                    "site_id": load_object.site_id,
                    "object_id": load_object.object_id,
                    "object_type": type(load_object).__name__,
                    "channel": "residual",
                    "expected_kw": object_expected_kw,
                    "actual_kw": object_actual_kw,
                    "expected_kwh": object_expected_kw * context.step_hours,
                    "actual_kwh": object_actual_kw * context.step_hours,
                    "is_controllable": False,
                    "is_observable_to_ml": False,
                }
            )

    return expected_kw, actual_kw
