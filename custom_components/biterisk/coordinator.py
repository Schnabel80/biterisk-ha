"""BiteRisk data update coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.storage import Store
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import const, scoring
from .brood import BroodBuffer

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class BiteRiskCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Reads weather sensors, computes mosquito risk every 5 minutes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=const.DOMAIN,
            update_interval=timedelta(minutes=const.UPDATE_INTERVAL_MINUTES),
        )
        self.entry = entry
        self._store: Store = Store(
            hass,
            const.STORAGE_VERSION,
            f"{const.STORAGE_KEY_BROOD}_{entry.entry_id}",
        )
        self.brood = BroodBuffer()
        self.warming_up = True
        self.brood_confidence = 0.0
        self._last_rain_total: float | None = None
        self._last_hour: int | None = None

    def _cfg(self, key: str, default: Any = None) -> Any:
        return self.entry.options.get(key, self.entry.data.get(key, default))

    def _read_float(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable", ""):
            return None
        try:
            return float(state.state)
        except ValueError, TypeError:
            return None

    def _minutes_from_sunset(self) -> float:
        sunset = get_astral_event_date(
            self.hass, "sunset", dt_util.now().date()
        )
        if sunset is None:
            return -360.0
        delta = dt_util.now() - sunset
        return delta.total_seconds() / 60.0

    def _ingest_rain(self) -> None:
        """Add new rain delta to the brood buffer, advancing per hour."""
        total = self._read_float(self._cfg(const.CONF_RAIN_SENSOR))
        now_hour = dt_util.now().hour
        if self._last_hour is not None and now_hour != self._last_hour:
            self.brood.advance_hours(1)
        self._last_hour = now_hour
        if total is None:
            return
        if (
            self._last_rain_total is not None
            and total >= self._last_rain_total
        ):
            self.brood.add_now(total - self._last_rain_total)
        self._last_rain_total = total

    async def _async_update_data(self) -> dict[str, Any]:
        self._ingest_rain()

        temp_c = self._read_float(self._cfg(const.CONF_TEMP_SENSOR))
        humidity = self._read_float(self._cfg(const.CONF_HUMIDITY_SENSOR))
        wind_ms = self._read_float(self._cfg(const.CONF_WIND_SENSOR))
        mins = self._minutes_from_sunset()
        floor = self._cfg(const.CONF_FLOOR, const.DEFAULT_FLOOR)

        f_brood = self.brood.score()
        f_temp = scoring.temp_factor(temp_c) if temp_c is not None else 0.0
        f_hum = (
            scoring.humidity_factor(humidity) if humidity is not None else 0.0
        )
        f_wind = scoring.wind_factor(wind_ms) if wind_ms is not None else 1.0
        f_time = scoring.time_factor(mins)

        raw = scoring.combine(
            brood=f_brood,
            temp=f_temp,
            humidity=f_hum,
            wind=f_wind,
            time=f_time,
            temp_c=temp_c,
            wind_ms=wind_ms,
        )
        risk_score = scoring.apply_floor(raw, floor)
        label = scoring.to_label(risk_score)

        await self._store.async_save(
            {
                "brood": self.brood.to_dict(),
                "last_rain_total": self._last_rain_total,
            }
        )

        return {
            "risk": label,
            "score": round(risk_score, 1),
            "factor_brood": round(f_brood, 3),
            "factor_temp": round(f_temp, 3),
            "factor_humidity": round(f_hum, 3),
            "factor_wind": round(f_wind, 3),
            "factor_time": round(f_time, 3),
            "warming_up": self.warming_up,
            "brood_confidence": round(self.brood_confidence, 2),
        }
