"""Planning skeleton.

Future packages should implement 15-minute baseline plans and activation plans here.
"""

from __future__ import annotations

from .models import EnergyChannels


def clone_baseline_plan(plan: EnergyChannels) -> EnergyChannels:
    """Return the current baseline plan unchanged.

    This placeholder keeps P0001 small while giving later packages a stable module.
    """

    return plan
