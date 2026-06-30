"""High-level synthetic stock generation for P0002."""

from __future__ import annotations

from collections import Counter

from .base_load_factory import generate_base_load_objects_for_sites
from .base_load_objects import BaseLoadObject
from .population import Household, StockGenerationConfig, generate_households, with_site_load_objects


def generate_synthetic_stock(
    seed: int = 1,
    config: StockGenerationConfig | None = None,
) -> tuple[Household, ...]:
    """Generate households, sites and latent base-load objects."""

    households = generate_households(seed=seed, config=config)
    sites = tuple(site for household in households for site in household.sites)
    objects_by_site = generate_base_load_objects_for_sites(sites, seed=seed + 10_000)
    return with_site_load_objects(households, objects_by_site)


def summarize_stock(households: tuple[Household, ...]) -> dict[str, object]:
    """Return a compact debug summary for generated synthetic stock."""

    sites = [site for household in households for site in household.sites]
    load_objects: list[BaseLoadObject] = [
        load_object for site in sites for load_object in site.load_objects
    ]
    object_counts = Counter(type(load_object).__name__ for load_object in load_objects)
    persons_distribution = Counter(household.persons_count for household in households)
    sites_by_type = Counter(site.site_type for site in sites)
    sites_by_size = Counter(site.size_class for site in sites)

    return {
        "households": len(households),
        "sites_by_type": dict(sorted(sites_by_type.items())),
        "sites_by_size": dict(sorted(sites_by_size.items())),
        "persons_count_distribution": dict(sorted(persons_distribution.items())),
        "object_counts_by_type": dict(sorted(object_counts.items())),
        "average_object_count_per_site": round(len(load_objects) / len(sites), 2) if sites else 0.0,
    }
