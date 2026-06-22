"""BiteRisk sensor entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import const

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BiteRiskCoordinator


@dataclass(frozen=True)
class BiteRiskSensorDescription(SensorEntityDescription):
    """Descriptor for BiteRisk sensors."""

    data_key: str = ""


SENSOR_DESCRIPTIONS: tuple[BiteRiskSensorDescription, ...] = (
    BiteRiskSensorDescription(
        key="risk",
        name="Mosquito Risk",
        icon="mdi:bug",
        data_key="risk",
    ),
    BiteRiskSensorDescription(
        key="score",
        name="Mosquito Score",
        icon="mdi:gauge",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="score",
    ),
    BiteRiskSensorDescription(
        key="factor_brood",
        name="Brood Factor",
        icon="mdi:water",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        data_key="factor_brood",
    ),
    BiteRiskSensorDescription(
        key="factor_temp",
        name="Temperature Factor",
        icon="mdi:thermometer",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        data_key="factor_temp",
    ),
    BiteRiskSensorDescription(
        key="factor_humidity",
        name="Humidity Factor",
        icon="mdi:water-percent",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        data_key="factor_humidity",
    ),
    BiteRiskSensorDescription(
        key="factor_wind",
        name="Wind Factor",
        icon="mdi:weather-windy",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        data_key="factor_wind",
    ),
    BiteRiskSensorDescription(
        key="factor_time",
        name="Time Factor",
        icon="mdi:clock-outline",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        data_key="factor_time",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: BiteRiskCoordinator = entry.runtime_data
    async_add_entities(
        BiteRiskSensor(coordinator, entry, desc)
        for desc in SENSOR_DESCRIPTIONS
    )


class BiteRiskSensor(CoordinatorEntity, SensorEntity):
    """A single BiteRisk sensor entity."""

    entity_description: BiteRiskSensorDescription

    def __init__(
        self,
        coordinator: BiteRiskCoordinator,
        entry: ConfigEntry,
        description: BiteRiskSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(const.DOMAIN, entry.entry_id)},
            "name": "BiteRisk",
            "manufacturer": "BiteRisk",
            "model": "Mosquito Risk Sensor",
        }

    @property
    def native_value(self) -> Any:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        if self.entity_description.key == "risk":
            return {
                "score": self.coordinator.data.get("score"),
                "warming_up": self.coordinator.data.get("warming_up"),
            }
        if self.entity_description.key == "factor_brood":
            return {
                "warming_up": self.coordinator.data.get("warming_up"),
                "brood_confidence": self.coordinator.data.get(
                    "brood_confidence"
                ),
            }
        return {}
