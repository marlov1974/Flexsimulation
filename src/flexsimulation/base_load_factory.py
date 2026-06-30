"""Factory for attaching synthetic latent base-load objects to sites."""

from __future__ import annotations

from random import Random

from .base_load_objects import (
    AlwaysLightObject,
    BaseLoadObject,
    ColdApplianceObject,
    InternetObject,
    StandbyClusterObject,
    TowelRailObject,
)
from .population import Site


def generate_base_load_objects_for_site(site: Site, rng: Random) -> tuple[BaseLoadObject, ...]:
    """Generate latent base-load objects for one site."""

    objects: list[BaseLoadObject] = []
    object_number = 1

    def next_object_id() -> str:
        nonlocal object_number
        object_id = f"{site.site_id}-L{object_number:03d}"
        object_number += 1
        return object_id

    cold_count = _sample_count(site, rng, small=1, medium=2, large_premium=3)
    for subtype in _cold_subtypes(cold_count):
        objects.append(
            ColdApplianceObject(
                object_id=next_object_id(),
                household_id=site.household_id,
                site_id=site.site_id,
                subtype=subtype,
                rated_kw=_cold_rated_kw(subtype) * site.site_random_factor,
                duty_cycle=0.25 if subtype == "fridge" else 0.35,
                cycle_length_steps=rng.choice((4, 6, 8)),
                phase_offset=rng.randrange(0, 8),
            )
        )

    internet_count = _sample_count(site, rng, small=1, medium=2, large_premium=3)
    for _ in range(internet_count):
        objects.append(
            InternetObject(
                object_id=next_object_id(),
                household_id=site.household_id,
                site_id=site.site_id,
                kw=rng.uniform(0.008, 0.025) * site.site_random_factor,
                noise_std_pct=0.04,
            )
        )

    site_cluster_count = {"small": 1, "medium": 2, "large_premium": 3}[site.size_class]
    if site.site_type == "cabin":
        site_cluster_count = max(1, site_cluster_count - 1)
    for _ in range(site_cluster_count):
        objects.append(_standby_cluster(next_object_id(), site, "site", rng))

    if site.site_role == "primary_home":
        for _ in range(site.persons_count):
            objects.append(_standby_cluster(next_object_id(), site, "person", rng))
    elif rng.random() < {"small": 0.25, "medium": 0.45, "large_premium": 0.65}[site.size_class]:
        objects.append(_standby_cluster(next_object_id(), site, "cabin_extra", rng))

    light_count = _sample_count(site, rng, small=1, medium=2, large_premium=3)
    for _ in range(light_count):
        objects.append(
            AlwaysLightObject(
                object_id=next_object_id(),
                household_id=site.household_id,
                site_id=site.site_id,
                on_probability_per_step=rng.uniform(0.55, 0.85),
            )
        )

    for _ in range(_towel_rail_count(site, rng)):
        objects.append(
            TowelRailObject(
                object_id=next_object_id(),
                household_id=site.household_id,
                site_id=site.site_id,
                kw=rng.uniform(0.05, 0.12) * site.site_random_factor,
                on_probability_per_step=rng.uniform(0.15, 0.45),
            )
        )

    return tuple(objects)


def generate_base_load_objects_for_sites(
    sites: tuple[Site, ...],
    seed: int = 1,
) -> dict[str, tuple[BaseLoadObject, ...]]:
    """Generate latent base-load objects keyed by site id."""

    rng = Random(seed)
    return {site.site_id: generate_base_load_objects_for_site(site, rng) for site in sites}


def _sample_count(
    site: Site,
    rng: Random,
    *,
    small: int,
    medium: int,
    large_premium: int,
) -> int:
    preferred = {"small": small, "medium": medium, "large_premium": large_premium}[site.size_class]
    if rng.random() < 0.20:
        preferred += rng.choice((-1, 1))
    return min(3, max(1, preferred))


def _cold_subtypes(count: int) -> tuple[str, ...]:
    if count == 1:
        return ("fridge_freezer",)
    if count == 2:
        return ("fridge", "freezer")
    return ("fridge", "freezer", "freezer")


def _cold_rated_kw(subtype: str) -> float:
    return {"fridge": 0.09, "freezer": 0.11, "fridge_freezer": 0.13}[subtype]


def _standby_cluster(
    object_id: str,
    site: Site,
    cluster_type: str,
    rng: Random,
) -> StandbyClusterObject:
    return StandbyClusterObject(
        object_id=object_id,
        household_id=site.household_id,
        site_id=site.site_id,
        cluster_type=cluster_type,
        unit_count=2,
        watt_per_unit=rng.uniform(2.0, 8.0) * site.site_random_factor,
        noise_std_pct=0.05,
    )


def _towel_rail_count(site: Site, rng: Random) -> int:
    probabilities = {
        "small": (0.65, 0.30, 0.05),
        "medium": (0.40, 0.45, 0.15),
        "large_premium": (0.20, 0.50, 0.30),
    }[site.size_class]
    if site.site_type == "cabin":
        probabilities = (probabilities[0] + 0.10, probabilities[1], max(0.0, probabilities[2] - 0.10))
    draw = rng.random()
    if draw < probabilities[0]:
        return 0
    if draw < probabilities[0] + probabilities[1]:
        return 1
    return 2
