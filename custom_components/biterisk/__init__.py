"""BiteRisk integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import (
    statistics_during_period,
)
from homeassistant.const import Platform
from homeassistant.util import dt as dt_util

from . import const
from .brood import BroodBuffer
from .coordinator import BiteRiskCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


async def _backfill_brood(
    hass: HomeAssistant, coordinator: BiteRiskCoordinator
) -> None:
    """Fill the brood buffer from long-term statistics on first start."""
    rain_entity = coordinator._cfg(const.CONF_RAIN_SENSOR)
    stored = await coordinator._store.async_load()
    if stored and stored.get("brood"):
        coordinator.brood = BroodBuffer.from_dict(stored["brood"])
        coordinator._last_rain_total = stored.get("last_rain_total")
        coordinator.warming_up = False
        coordinator.brood_confidence = 1.0
        return
    if not rain_entity:
        return

    start = dt_util.now() - timedelta(hours=const.BROOD_HOURS)
    try:
        stats = await get_instance(hass).async_add_executor_job(
            statistics_during_period,
            hass,
            start,
            None,
            {rain_entity},
            "hour",
            None,
            {"sum"},
        )
    except Exception:  # noqa: BLE001 - recorder may be unavailable
        _LOGGER.warning("BiteRisk: statistics backfill unavailable")
        return

    rows = stats.get(rain_entity, [])
    covered = 0
    now = dt_util.now()
    for row in rows:
        ts = dt_util.utc_from_timestamp(row["start"])
        hours_ago = int((now - ts).total_seconds() // 3600)
        mm = row.get("sum") or 0.0
        if 0 <= hours_ago < const.BROOD_HOURS:
            coordinator.brood.set_hour(hours_ago, float(mm))
            covered += 1
    coordinator.brood_confidence = min(1.0, covered / const.BROOD_HOURS)
    coordinator.warming_up = coordinator.brood_confidence < 1.0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = BiteRiskCoordinator(hass, entry)
    await _backfill_brood(hass, coordinator)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
