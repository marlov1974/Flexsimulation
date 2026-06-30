from datetime import datetime

from flexsimulation.simulation_time import (
    create_2025_time_index,
    create_simulation_contexts,
    stable_seed,
)


def test_create_2025_time_index_has_15_minute_full_year() -> None:
    timestamps = create_2025_time_index()

    assert len(timestamps) == 35_040
    assert timestamps[0] == datetime(2025, 1, 1, 0, 0)
    assert timestamps[-1] == datetime(2025, 12, 31, 23, 45)


def test_simulation_context_has_time_properties() -> None:
    context = create_simulation_contexts((datetime(2025, 6, 2, 10, 30),))[0]

    assert context.step_hours == 0.25
    assert context.month == 6
    assert context.weekday == 0
    assert context.hour == 10
    assert context.minute == 30
    assert context.quarter_of_day == 42


def test_stable_seed_is_deterministic_and_object_specific() -> None:
    assert stable_seed(1, 10, "O1") == stable_seed(1, 10, "O1")
    assert stable_seed(1, 10, "O1") != stable_seed(1, 10, "O2")
