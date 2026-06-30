from flexsimulation.population import (
    SITE_CONFIGURATIONS,
    SITE_ROLES,
    SITE_TYPES,
    SIZE_CLASSES,
    StockGenerationConfig,
    generate_households,
)


def test_generate_households_is_reproducible() -> None:
    config = StockGenerationConfig(households=25)

    assert generate_households(seed=42, config=config) == generate_households(seed=42, config=config)


def test_generate_households_has_valid_required_fields() -> None:
    households = generate_households(seed=7, config=StockGenerationConfig(households=50))

    assert len(households) == 50
    for household in households:
        assert household.persons_count in {2, 3, 4, 5}
        assert household.site_configuration in SITE_CONFIGURATIONS
        assert len(household.sites) >= 1
        assert not hasattr(household, "persons_class")
        for site in household.sites:
            assert site.household_id == household.household_id
            assert site.site_role in SITE_ROLES
            assert site.site_type in SITE_TYPES
            assert site.size_class in SIZE_CLASSES
            assert 0.85 <= site.site_random_factor <= 1.20


def test_site_configuration_mapping() -> None:
    expected_site_types = {
        "apartment_only": ("apartment",),
        "house_only": ("house",),
        "cabin_only": ("cabin",),
        "apartment_plus_cabin": ("apartment", "cabin"),
        "house_plus_cabin": ("house", "cabin"),
    }

    for site_configuration, site_types in expected_site_types.items():
        households = generate_households(
            seed=3,
            config=StockGenerationConfig(
                households=1,
                site_configuration_weights={site_configuration: 1.0},
            ),
        )

        assert tuple(site.site_type for site in households[0].sites) == site_types
