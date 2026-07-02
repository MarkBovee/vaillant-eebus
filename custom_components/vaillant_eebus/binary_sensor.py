"""Binary sensor platform for Vaillant EEBUS."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VaillantCoordinator

_LOGGER = logging.getLogger(__name__)


def _is_compressor_running(data: dict[str, dict[str, Any]]) -> bool:
    """Check if compressor is running."""
    for item in data.values():
        scope = (item.get("scopeType") or "").lower()
        val = item.get("value")
        if isinstance(val, (int, float)):
            if "acpowertotal" in scope and val > 0:
                return True
            if "compressorfrequency" in scope and val > 0:
                return True
    return False


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[VaillantBinarySensor] = []

    entities.append(
        VaillantBinarySensor(
            coordinator,
            "compressor_running",
            "Compressor Running",
            BinarySensorDeviceClass.RUNNING,
            entry,
        )
    )

    async_add_entities(entities)


class VaillantBinarySensor(
    CoordinatorEntity[VaillantCoordinator], BinarySensorEntity
):
    """Binary sensor representing a Vaillant state."""

    def __init__(
        self,
        coordinator: VaillantCoordinator,
        object_id: str,
        name: str,
        device_class: BinarySensorDeviceClass | str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self._object_id = object_id
        self._attr_unique_id = f"{entry.entry_id}_{object_id}"
        self._attr_name = name
        self._attr_has_entity_name = True
        self._attr_device_class = device_class
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if compressor is running."""
        return _is_compressor_running(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.client.connected
