"""Business-case result models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessCaseResult:
    """Minimal business-case result placeholder."""

    scenario_id: str
    households: int
    net_value_sek: float

    @property
    def net_value_per_customer_sek(self) -> float:
        """Return net value per simulated customer."""

        if self.households == 0:
            return 0.0
        return self.net_value_sek / self.households
