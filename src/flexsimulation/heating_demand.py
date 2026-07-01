"""Weather-driven heating demand model for P0005."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeatingDemandModel:
    """Convert outdoor temperature into non-negative thermal demand."""

    balance_temperature_c: float
    design_temperature_c: float
    design_heat_loss_kw: float
    internal_gain_kw: float = 0.0

    def thermal_need_kw(self, outdoor_temp_c: float) -> float:
        """Return thermal heating need in kW."""

        denominator = self.balance_temperature_c - self.design_temperature_c
        if denominator <= 0:
            raise ValueError("balance_temperature_c must exceed design_temperature_c")
        heat_loss_slope_kw_per_c = self.design_heat_loss_kw / denominator
        thermal_need_kw = (
            heat_loss_slope_kw_per_c * (self.balance_temperature_c - outdoor_temp_c)
            - self.internal_gain_kw
        )
        return max(0.0, thermal_need_kw)
