from collections import Counter
from random import Random

from flexsimulation.base_load_factory import generate_base_load_objects_for_site
from flexsimulation.base_load_objects import (
    AlwaysLightObject,
    ColdApplianceObject,
    InternetObject,
    StandbyClusterObject,
    TowelRailObject,
)
from flexsimulation.population import Site
from flexsimulation.stock_generator import generate_synthetic_stock, summarize_stock


def test_generate_base_load_objects_for_site_meets_count_rules() -> None:
    site = Site(
        site_id="H0001-S1",
        household_id=1,
        site_role="primary_home",
        site_type="house",
        size_class="medium",
        persons_count=4,
        site_random_factor=1.0,
    )

    objects = generate_base_load_objects_for_site(site, Random(4))
    counts = Counter(type(load_object) for load_object in objects)

    assert 1 <= counts[ColdApplianceObject] <= 3
    assert 1 <= counts[InternetObject] <= 3
    assert counts[StandbyClusterObject] >= site.persons_count + 1
    assert 1 <= counts[AlwaysLightObject] <= 3
    assert 0 <= counts[TowelRailObject] <= 2
    assert all(
        load_object.unit_count == 2
        for load_object in objects
        if isinstance(load_object, StandbyClusterObject)
    )
    assert all(
        load_object.kw == 0.05
        for load_object in objects
        if isinstance(load_object, AlwaysLightObject)
    )


def test_large_premium_sites_tend_to_get_more_selected_objects_than_small_sites() -> None:
    small_total = 0
    large_total = 0

    for seed in range(100):
        small_site = Site("S-small", 1, "primary_home", "house", "small", 4, 1.0)
        large_site = Site("S-large", 1, "primary_home", "house", "large_premium", 4, 1.0)
        small_objects = generate_base_load_objects_for_site(small_site, Random(seed))
        large_objects = generate_base_load_objects_for_site(large_site, Random(seed))

        small_total += _selected_object_count(small_objects)
        large_total += _selected_object_count(large_objects)

    assert large_total > small_total


def test_generate_synthetic_stock_attaches_reproducible_latent_objects() -> None:
    stock = generate_synthetic_stock(seed=11)
    repeated_stock = generate_synthetic_stock(seed=11)

    assert stock == repeated_stock
    assert len(stock) == 100
    assert all(site.load_objects for household in stock for site in household.sites)


def test_stock_summary_contains_debug_counts() -> None:
    summary = summarize_stock(generate_synthetic_stock(seed=11))

    assert summary["households"] == 100
    assert summary["average_object_count_per_site"] > 0
    assert "ColdApplianceObject" in summary["object_counts_by_type"]


def _selected_object_count(objects: tuple[object, ...]) -> int:
    selected_types = (InternetObject, AlwaysLightObject, TowelRailObject)
    return sum(isinstance(load_object, selected_types) for load_object in objects)
