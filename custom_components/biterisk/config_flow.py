"""Config flow for BiteRisk integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from . import const

STEP_SENSORS_SCHEMA = vol.Schema(
    {
        vol.Required(const.CONF_TEMP_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
        vol.Required(const.CONF_HUMIDITY_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
        vol.Required(const.CONF_WIND_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
        vol.Required(const.CONF_RAIN_SENSOR): selector.selector(
            {"entity": {"domain": "sensor"}}
        ),
    }
)

STEP_LOCATION_SCHEMA = vol.Schema(
    {
        vol.Required(
            const.CONF_FLOOR, default=const.DEFAULT_FLOOR
        ): selector.selector(
            {
                "select": {
                    "options": [
                        const.FLOOR_GROUND,
                        const.FLOOR_FIRST,
                        const.FLOOR_SECOND_PLUS,
                    ]
                }
            }
        ),
        vol.Optional(
            const.CONF_SUN_ENTITY, default=const.DEFAULT_SUN_ENTITY
        ): selector.selector({"entity": {"domain": "sun"}}),
    }
)


class BiteRiskConfigFlow(ConfigFlow, domain=const.DOMAIN):
    """Two-step config flow: sensors → location."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_location()
        return self.async_show_form(
            step_id="user", data_schema=STEP_SENSORS_SCHEMA
        )

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="BiteRisk", data=self._data)
        return self.async_show_form(
            step_id="location", data_schema=STEP_LOCATION_SCHEMA
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return BiteRiskOptionsFlow(config_entry)


class BiteRiskOptionsFlow(OptionsFlow):
    """Options flow to change floor/sensors after setup."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema(
            {
                vol.Required(
                    const.CONF_FLOOR,
                    default=self._config_entry.options.get(
                        const.CONF_FLOOR,
                        self._config_entry.data.get(
                            const.CONF_FLOOR, const.DEFAULT_FLOOR
                        ),
                    ),
                ): selector.selector(
                    {
                        "select": {
                            "options": [
                                const.FLOOR_GROUND,
                                const.FLOOR_FIRST,
                                const.FLOOR_SECOND_PLUS,
                            ]
                        }
                    }
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
