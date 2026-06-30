"""Synthetic household and site population generation for P0002."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from random import Random
from typing import Any


SITE_CONFIGURATIONS = (
    "apartment_only",
    "house_only",
    "cabin_only",
    "apartment_plus_cabin",
    "house_plus_cabin",
)
SITE_ROLES = ("primary_home", "cabin")
SITE_TYPES = ("apartment", "house", "cabin")
SIZE_CLASSES = ("small", "medium", "large_premium")


@dataclass(frozen=True)
class Site:
    """Synthetic electricity location."""

    site_id: str
    household_id: int
    site_role: str
    site_type: str
    size_class: str
    persons_count: int
    site_random_factor: float
    load_objects: tuple[Any, ...] = ()
    asset_objects: tuple[Any, ...] = ()


@dataclass(frozen=True)
class Household:
    """Customer-level synthetic entity."""

    household_id: int
    persons_count: int
    site_configuration: str
    sites: tuple[Site, ...]


@dataclass(frozen=True)
class StockGenerationConfig:
    """Configurable synthetic stock generation settings."""

    households: int = 100
    persons_count_weights: dict[int, float] = field(
        default_factory=lambda: {2: 0.15, 3: 0.25, 4: 0.35, 5: 0.25}
    )
    site_configuration_weights: dict[str, float] = field(
        default_factory=lambda: {
            "apartment_only": 0.25,
            "house_only": 0.30,
            "cabin_only": 0.05,
            "apartment_plus_cabin": 0.15,
            "house_plus_cabin": 0.25,
        }
    )
    site_random_factor_min: float = 0.85
    site_random_factor_max: float = 1.20


def generate_households(
    seed: int = 1,
    config: StockGenerationConfig | None = None,
) -> tuple[Household, ...]:
    """Generate reproducible synthetic households and sites."""

    resolved_config = config or StockGenerationConfig()
    rng = Random(seed)
    households: list[Household] = []

    for household_id in range(1, resolved_config.households + 1):
        persons_count = _weighted_choice(resolved_config.persons_count_weights, rng)
        site_configuration = _weighted_choice(resolved_config.site_configuration_weights, rng)
        sites = _create_sites(household_id, persons_count, site_configuration, resolved_config, rng)
        households.append(
            Household(
                household_id=household_id,
                persons_count=persons_count,
                site_configuration=site_configuration,
                sites=sites,
            )
        )

    return tuple(households)


def with_site_load_objects(
    households: tuple[Household, ...],
    load_objects_by_site_id: dict[str, tuple[Any, ...]],
) -> tuple[Household, ...]:
    """Return households with latent load objects attached to matching sites."""

    updated_households: list[Household] = []
    for household in households:
        updated_sites = tuple(
            replace(site, load_objects=load_objects_by_site_id.get(site.site_id, site.load_objects))
            for site in household.sites
        )
        updated_households.append(replace(household, sites=updated_sites))
    return tuple(updated_households)


def _create_sites(
    household_id: int,
    persons_count: int,
    site_configuration: str,
    config: StockGenerationConfig,
    rng: Random,
) -> tuple[Site, ...]:
    site_specs = {
        "apartment_only": (("primary_home", "apartment"),),
        "house_only": (("primary_home", "house"),),
        "cabin_only": (("cabin", "cabin"),),
        "apartment_plus_cabin": (("primary_home", "apartment"), ("cabin", "cabin")),
        "house_plus_cabin": (("primary_home", "house"), ("cabin", "cabin")),
    }[site_configuration]

    sites: list[Site] = []
    primary_home_size = "medium"
    for site_index, (site_role, site_type) in enumerate(site_specs, start=1):
        size_class = _sample_size(site_type, persons_count, primary_home_size, rng)
        if site_role == "primary_home":
            primary_home_size = size_class
        site_random_factor = rng.uniform(
            config.site_random_factor_min,
            config.site_random_factor_max,
        )
        site_random_factor = min(
            config.site_random_factor_max,
            max(config.site_random_factor_min, site_random_factor),
        )
        sites.append(
            Site(
                site_id=f"H{household_id:04d}-S{site_index}",
                household_id=household_id,
                site_role=site_role,
                site_type=site_type,
                size_class=size_class,
                persons_count=persons_count,
                site_random_factor=round(site_random_factor, 4),
            )
        )
    return tuple(sites)


def _sample_size(
    site_type: str,
    persons_count: int,
    primary_home_size: str,
    rng: Random,
) -> str:
    weights_by_type = {
        "apartment": {"small": 0.45, "medium": 0.45, "large_premium": 0.10},
        "house": {"small": 0.20, "medium": 0.50, "large_premium": 0.30},
        "cabin": {"small": 0.35, "medium": 0.45, "large_premium": 0.20},
    }
    weights = dict(weights_by_type[site_type])

    if persons_count >= 4:
        weights["small"] *= 0.65
        weights["medium"] *= 1.10
        weights["large_premium"] *= 1.35
    elif persons_count == 2:
        weights["small"] *= 1.35
        weights["large_premium"] *= 0.70

    if site_type == "cabin" and primary_home_size == "large_premium":
        weights["medium"] *= 1.10
        weights["large_premium"] *= 1.35

    return _weighted_choice(weights, rng)


def _weighted_choice[T](weights: dict[T, float], rng: Random) -> T:
    if not weights:
        raise ValueError("weights must not be empty")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must have a positive total")

    threshold = rng.random() * total
    cumulative = 0.0
    last_key: T | None = None
    for key, weight in weights.items():
        if weight < 0:
            raise ValueError("weights must not be negative")
        cumulative += weight
        last_key = key
        if threshold <= cumulative:
            return key

    if last_key is None:
        raise ValueError("weights must not be empty")
    return last_key
