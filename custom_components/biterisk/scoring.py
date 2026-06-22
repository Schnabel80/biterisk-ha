"""Pure mosquito-risk scoring. No Home Assistant imports."""

from __future__ import annotations

from . import const


def temp_factor(temp_c: float) -> float:
    if temp_c <= const.TEMP_MIN_ACTIVE or temp_c >= const.TEMP_MAX_ACTIVE:
        return 0.0
    if const.TEMP_OPT_LOW <= temp_c <= const.TEMP_OPT_HIGH:
        return 1.0
    if temp_c < const.TEMP_OPT_LOW:
        span = const.TEMP_OPT_LOW - const.TEMP_MIN_ACTIVE
        return (temp_c - const.TEMP_MIN_ACTIVE) / span
    span = const.TEMP_MAX_ACTIVE - const.TEMP_OPT_HIGH
    return (const.TEMP_MAX_ACTIVE - temp_c) / span


def humidity_factor(humidity_pct: float) -> float:
    if humidity_pct <= const.HUMIDITY_MIN:
        return 0.0
    if humidity_pct >= const.HUMIDITY_FULL:
        return 1.0
    span = const.HUMIDITY_FULL - const.HUMIDITY_MIN
    return (humidity_pct - const.HUMIDITY_MIN) / span


def wind_factor(wind_ms: float) -> float:
    if wind_ms <= const.WIND_FULL_BELOW:
        return 1.0
    if wind_ms >= const.WIND_ZERO_AT:
        return 0.0
    span = const.WIND_ZERO_AT - const.WIND_FULL_BELOW
    return (const.WIND_ZERO_AT - wind_ms) / span


def time_factor(minutes_from_sunset: float) -> float:
    """Crepuscular bell. 0 = sunset; peak window [-DUSK_PRE, +DUSK_POST]."""
    if -const.DUSK_PRE_MIN <= minutes_from_sunset <= const.DUSK_POST_MIN:
        return const.TIME_PEAK
    if minutes_from_sunset < -const.DUSK_PRE_MIN:
        return const.TIME_DAY_BASE
    return const.TIME_NIGHT_BASE


def combine(
    *,
    brood: float,
    temp: float,
    humidity: float,
    wind: float,
    time: float,
    temp_c: float | None = None,
    wind_ms: float | None = None,
) -> float:
    """Weighted sum -> 0..100, with hard K.O. cutoffs."""
    if temp_c is not None and (
        temp_c < const.TEMP_MIN_ACTIVE or temp_c > const.TEMP_MAX_ACTIVE
    ):
        return 0.0
    if wind_ms is not None and wind_ms >= const.WIND_ZERO_AT:
        return 0.0
    total = (
        brood * const.WEIGHT_BROOD
        + temp * const.WEIGHT_TEMP
        + humidity * const.WEIGHT_HUMIDITY
        + wind * const.WEIGHT_WIND
        + time * const.WEIGHT_TIME
    )
    return max(0.0, min(100.0, total * 100.0))


def apply_floor(score: float, floor: str) -> float:
    mod = const.FLOOR_MODIFIERS.get(floor, 1.0)
    return score * mod


def to_label(score: float) -> str:
    if score <= const.LABEL_LOW_MAX:
        return const.RISK_LOW
    if score <= const.LABEL_MED_MAX:
        return const.RISK_MEDIUM
    return const.RISK_HIGH
