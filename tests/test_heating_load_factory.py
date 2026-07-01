from collections import Counter
from random import Random

from flexsimulation.heating_load_factory import (
    HeatingLoadGenerationConfig,
    add_uncontrolled_heating_objects,
    generate_uncontrolled_heating_objects_for_site,
)
from flexsimulation.heating_load_objects import HEATING_LOAD_OBJECT_TYPES
from flexsimulation.population import Site, StockGenerationConfig
from flexsimulation.stock_generator import generate_synthetic_stock


def test_heating_factory_eligibility_rules() -> None:
    apartment = Site("A1", 1, "primary_home", "apartment", "medium", 3, 1.0)
    house = Site("H1", 1, "primary_home", "house", "medium", 4, 1.0)
    cabin = Site("C1", 1, "cabin", "cabin", "small", 2, 1.0)

    assert generate_uncontrolled_heating_objects_for_site(apartment, Random(1)) == ()
    assert len(generate_uncontrolled_heating_objects_for_site(house, Random(1))) == 1
    assert len(generate_uncontrolled_heating_objects_for_site(cabin, Random(1))) == 1


def test_default_heating_weights_are_configurable_and_match_proxy_assumptions() -> None:
    config = HeatingLoadGenerationConfig()

    assert config.heating_type_weights["apartment"] == {"none": 1.0}
    assert config.heating_type_weights["house"]["ground_source_heat_pump"] == 0.30
    assert config.heating_type_weights["cabin"]["direct_electric"] == 0.45


def test_heating_generation_is_reproducible_and_appends_to_house_cabin_only() -> None:
    households = generate_synthetic_stock(seed=3, config=StockGenerationConfig(households=20))

    first = add_uncontrolled_heating_objects(households, seed=99)
    second = add_uncontrolled_heating_objects(households, seed=99)

    assert first == second
    counts = Counter()
    for household in first:
        for site in household.sites:
            heating_objects = [
                load_object
                for load_object in site.load_objects
                if isinstance(load_object, HEATING_LOAD_OBJECT_TYPES)
            ]
            counts[site.site_type] += len(heating_objects)
            if site.site_type == "apartment":
                assert not heating_objects
            else:
                assert len(heating_objects) == 1
                assert heating_objects[0].heating_role == "primary"

    assert counts["house"] > 0
    assert counts["cabin"] > 0
