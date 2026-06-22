"""Pure brood-population model. No Home Assistant imports."""

from __future__ import annotations

from . import const


def _lag_weight(hours_ago: int) -> float:
    """Weight a rain hour by larval-development lag.

    Ramp up from 0 at hour 0 to 1.0 at LAG_PEAK_START_H, plateau through
    LAG_PEAK_END_H, then linear decay to 0 at the end of the buffer.
    """
    if hours_ago <= 0:
        return 0.0
    if hours_ago < const.LAG_PEAK_START_H:
        return hours_ago / const.LAG_PEAK_START_H
    if hours_ago <= const.LAG_PEAK_END_H:
        return 1.0
    span = const.BROOD_HOURS - const.LAG_PEAK_END_H
    if span <= 0:
        return 0.0
    decayed = 1.0 - (hours_ago - const.LAG_PEAK_END_H) / span
    return max(0.0, decayed)


class BroodBuffer:
    """Rolling 21-day hourly rain buffer, index = hours ago (0 = now)."""

    def __init__(self, slots: list[float] | None = None) -> None:
        self._slots = slots if slots is not None else [0.0] * const.BROOD_HOURS

    def set_hour(self, hours_ago: int, mm: float) -> None:
        if 0 <= hours_ago < const.BROOD_HOURS:
            self._slots[hours_ago] = max(0.0, mm)

    def get_hour(self, hours_ago: int) -> float:
        if 0 <= hours_ago < const.BROOD_HOURS:
            return self._slots[hours_ago]
        return 0.0

    def add_now(self, mm: float) -> None:
        """Accumulate rain into the current hour (index 0)."""
        self._slots[0] += max(0.0, mm)

    def advance_hours(self, hours: int) -> None:
        """Shift the buffer by N hours (older), zero-filling the front."""
        if hours <= 0:
            return
        hours = min(hours, const.BROOD_HOURS)
        self._slots = [0.0] * hours + self._slots[: const.BROOD_HOURS - hours]

    def score(self) -> float:
        """Lag-weighted, wash-out-capped brood population score in [0,1]."""
        weighted = 0.0
        for hours_ago, mm in enumerate(self._slots):
            capped = min(mm, const.HEAVY_RAIN_CAP_MM)
            weighted += capped * _lag_weight(hours_ago)
        return min(1.0, weighted / const.BROOD_SATURATION_MM)

    def to_dict(self) -> dict:
        return {"slots": self._slots}

    @classmethod
    def from_dict(cls, data: dict) -> BroodBuffer:
        slots = list(data.get("slots", []))
        if len(slots) != const.BROOD_HOURS:
            slots = (slots + [0.0] * const.BROOD_HOURS)[: const.BROOD_HOURS]
        return cls(slots)
