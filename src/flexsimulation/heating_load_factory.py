"""Factory for uncontrolled heating load objects."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from random import Random

from .heating_demand import HeatingDemandModel
from .heating_load_objects import (
    AirAirHeatPumpLoadObject,
    AirWaterHeatPumpLoadObject,
    DirectElectricHeatingObject,
    ExhaustAirHeatPumpLoadObject,
    GroundSourceHeatPumpLoadObject,
    HeatingLoadObject,
    PelletStoveLoadObject,
)
from .population import Household, Site


@dataclass(frozen=True)
class HeatingLoadGenerationConfig:
    """Configurable synthetic heating assumptions."""

    heating_type_weights: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            "house": {
                "ground_source_heat_pump": 0.30,
                "air_water_heat_pump": 0.18,
                "exhaust_air_heat_pump": 0.12,
                "direct_electric": 0.20,
                "air_air_heat_pump": 0.15,
                "pellet_stove": 0.05,
            },
            "cabin": {
                "direct_electric": 0.45,
                "air_air_heat_pump": 0.35,
                "pellet_stove": 0.15,
                "air_water_heat_pump": 0.05,
            },
            "apartment": {"none": 1.00},
        }
    )
    design_heat_loss_kw: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            "house": {"small": 6.0, "medium": 10.0, "large_premium": 16.0},
            "cabin": {"small": 3.0, "medium": 6.0, "large_premium": 10.0},
            "apartment": {"small": 2.0, "medium": 4.0, "large_premium": 6.0},
        }
    )
    balance_temperature_c: dict[str, float] = field(
        default_factory=lambda: {"house": 15.0, "cabin": 10.0, "apartment": 15.0}
    )
    design_temperature_c: dict[str, float] = field(
        default_factory=lambda: {"house": -15.0, "cabin": -15.0, "apartment": -15.0}
    )
    internal_gain_kw: dict[str, float] = field(
        default_factory=lambda: {"house": 0.8, "cabin": 0.2, "apartment": 0.5}
    )


def generate_uncontrolled_heating_objects_for_site(
    site: Site,
    rng: Random,
    config: HeatingLoadGenerationConfig | None = None,
) -> tuple[HeatingLoadObject, ...]:
    """Generate P0005 uncontrolled heating object for an eligible site."""

    resolved_config = config or HeatingLoadGenerationConfig()
    if site.site_type == "apartment":
        return ()

    heating_type = _weighted_choice(resolved_config.heating_type_weights[site.site_type], rng)
    if heating_type == "none":
        return ()

    demand_model = _demand_model_for_site(site, resolved_config)
    object_id = f"{site.site_id}-H001"
    return (_create_heating_object(object_id, site, heating_type, demand_model),)


def generate_uncontrolled_heating_objects_for_sites(
    sites: tuple[Site, ...],
    seed: int = 1,
    config: HeatingLoadGenerationConfig | None = None,
) -> dict[str, tuple[HeatingLoadObject, ...]]:
    """Generate uncontrolled heating objects keyed by site id."""

    rng = Random(seed)
    return {
        site.site_id: generate_uncontrolled_heating_objects_for_site(site, rng, config)
        for site in sites
    }


def add_uncontrolled_heating_objects(
    households: tuple[Household, ...],
    seed: int = 1,
    config: HeatingLoadGenerationConfig | None = None,
) -> tuple[Household, ...]:
    """Return households with P0005 heating load objects appended."""

    sites = tuple(site for household in households for site in household.sites)
    heating_by_site = generate_uncontrolled_heating_objects_for_sites(sites, seed=seed, config=config)
    updated_households: list[Household] = []
    for household in households:
        updated_sites = []
        for site in household.sites:
            heating_objects = heating_by_site.get(site.site_id, ())
            updated_sites.append(replace(site, load_objects=site.load_objects + heating_objects))
        updated_households.append(replace(household, sites=tuple(updated_sites)))
    return tuple(updated_households)


def _demand_model_for_site(
    site: Site,
    config: HeatingLoadGenerationConfig,
) -> HeatingDemandModel:
    design_heat_loss_kw = (
        config.design_heat_loss_kw[site.site_type][site.size_class] * site.site_random_factor
    )
    return HeatingDemandModel(
        balance_temperature_c=config.balance_temperature_c[site.site_type],
        design_temperature_c=config.design_temperature_c[site.site_type],
        design_heat_loss_kw=design_heat_loss_kw,
        internal_gain_kw=config.internal_gain_kw[site.site_type],
    )


def _create_heating_object(
    object_id: str,
    site: Site,
    heating_type: str,
    demand_model: HeatingDemandModel,
) -> HeatingLoadObject:
    design_heat_loss_kw = demand_model.design_heat_loss_kw
    if heating_type == "direct_electric":
        return DirectElectricHeatingObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            max_electric_kw=design_heat_loss_kw * 1.15,
            demand_model=demand_model,
            noise_std_pct=0.05,
        )
    if heating_type == "ground_source_heat_pump":
        return GroundSourceHeatPumpLoadObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            max_thermal_output_kw=design_heat_loss_kw * 0.85,
            nominal_cop=4.0,
            min_cop=2.6,
            load_cop_penalty=0.6,
            backup_electric_kw=design_heat_loss_kw * 0.35,
            demand_model=demand_model,
            noise_std_pct=0.04,
        )
    if heating_type == "air_air_heat_pump":
        return AirAirHeatPumpLoadObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            max_thermal_output_kw_at_7c=design_heat_loss_kw * 0.65,
            backup_electric_kw=design_heat_loss_kw * 0.55,
            demand_model=demand_model,
            noise_std_pct=0.06,
            cold_noise_multiplier=1.8,
        )
    if heating_type == "air_water_heat_pump":
        return AirWaterHeatPumpLoadObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            max_thermal_output_kw_at_7c=design_heat_loss_kw * 0.80,
            backup_electric_kw=design_heat_loss_kw * 0.45,
            demand_model=demand_model,
            noise_std_pct=0.055,
            cold_noise_multiplier=1.7,
        )
    if heating_type == "exhaust_air_heat_pump":
        return ExhaustAirHeatPumpLoadObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            recovery_thermal_kw=design_heat_loss_kw * 0.30,
            cop=2.6,
            backup_electric_kw=design_heat_loss_kw * 0.75,
            demand_model=demand_model,
            noise_std_pct=0.05,
        )
    if heating_type == "pellet_stove":
        return PelletStoveLoadObject(
            object_id=object_id,
            household_id=site.household_id,
            site_id=site.site_id,
            running_thermal_need_threshold_kw=0.8 if site.site_type == "cabin" else 1.2,
            thermal_output_kw=design_heat_loss_kw * 0.75,
            demand_model=demand_model,
            noise_std_pct=0.03,
        )
    raise ValueError(f"unsupported heating_type: {heating_type}")


def _weighted_choice(weights: dict[str, float], rng: Random) -> str:
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must have a positive total")
    threshold = rng.random() * total
    cumulative = 0.0
    last_key = ""
    for key, weight in weights.items():
        if weight < 0:
            raise ValueError("weights must not be negative")
        cumulative += weight
        last_key = key
        if threshold <= cumulative:
            return key
    return last_key
