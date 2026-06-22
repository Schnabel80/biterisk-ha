"""Tests for BiteRisk config flow."""

from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.biterisk import const


async def test_config_flow_full(hass, enable_custom_integrations):
    """Two-step flow creates entry with sensor + location data."""
    result = await hass.config_entries.flow.async_init(
        const.DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            const.CONF_TEMP_SENSOR: "sensor.temp",
            const.CONF_HUMIDITY_SENSOR: "sensor.humidity",
            const.CONF_WIND_SENSOR: "sensor.wind",
            const.CONF_RAIN_SENSOR: "sensor.rain",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "location"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            const.CONF_FLOOR: const.FLOOR_GROUND,
            const.CONF_SUN_ENTITY: const.DEFAULT_SUN_ENTITY,
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][const.CONF_TEMP_SENSOR] == "sensor.temp"
    assert result["data"][const.CONF_FLOOR] == const.FLOOR_GROUND


async def test_options_flow(hass, enable_custom_integrations):
    """Options flow changes floor modifier."""
    entry = MockConfigEntry(
        domain=const.DOMAIN,
        data={
            const.CONF_TEMP_SENSOR: "sensor.temp",
            const.CONF_HUMIDITY_SENSOR: "sensor.humidity",
            const.CONF_WIND_SENSOR: "sensor.wind",
            const.CONF_RAIN_SENSOR: "sensor.rain",
            const.CONF_FLOOR: const.FLOOR_GROUND,
            const.CONF_SUN_ENTITY: const.DEFAULT_SUN_ENTITY,
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={const.CONF_FLOOR: const.FLOOR_FIRST},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[const.CONF_FLOOR] == const.FLOOR_FIRST
