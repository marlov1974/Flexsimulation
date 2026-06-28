"""Activation accounting helpers."""

from __future__ import annotations

from .models import ResponseAccounting


def calculate_response_kw(baseline_power_kw: float, actual_power_kw: float) -> float:
    """Calculate response as baseline minus actual."""

    return ResponseAccounting(
        baseline_power_kw=baseline_power_kw,
        actual_power_kw=actual_power_kw,
    ).response_kw
