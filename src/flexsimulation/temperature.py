"""Synthetic temperature providers for P0005."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class TemperatureProvider(Protocol):
    """Abstraction for outdoor temperature sources."""

    def outdoor_temp_c(self, timestamp: datetime) -> float:
        """Return outdoor temperature in degrees C."""


@dataclass(frozen=True)
class SyntheticTemperatureProvider:
    """Public-safe synthetic Nordic temperature provider."""

    annual_mean_c: float = 5.0
    seasonal_amplitude_c: float = 13.0
    daily_amplitude_c: float = 2.0
    coldest_day_of_year: int = 20

    def outdoor_temp_c(self, timestamp: datetime) -> float:
        """Return plausible synthetic outdoor temperature for a timestamp."""

        day_of_year = timestamp.timetuple().tm_yday
        seasonal_angle = 2.0 * math.pi * (day_of_year - self.coldest_day_of_year) / 365.0
        seasonal = self.annual_mean_c - self.seasonal_amplitude_c * math.cos(seasonal_angle)
        hour = timestamp.hour + timestamp.minute / 60.0
        daily_angle = 2.0 * math.pi * (hour - 15.0) / 24.0
        daily = self.daily_amplitude_c * math.cos(daily_angle)
        return round(seasonal + daily, 3)
