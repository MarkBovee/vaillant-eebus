"""Binary sensor platform for Vaillant EEBUS."""

from __future__ import annotations

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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for desc in coordinator.entities:
        if desc.entity_type != "binary_sensor":
            continue
        uid = f"{entry.entry_id}_{desc.unique_id}"
        entities.append(EbusdBinarySensor(coordinator, desc, uid, entry))

    async_add_entities(entities)


BINARY_TRUE_VALUES = {"on", "1", "true", "yes", "running", "day"}


class EbusdBinarySensor(CoordinatorEntity[VaillantCoordinator], BinarySensorEntity):
    def __init__(
        self,
        coordinator: VaillantCoordinator,
        desc: Any,
        unique_id: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._desc = desc
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_device_info = coordinator.get_device_info(desc.circuit)
        self._attr_name = desc.meta.friendly_name or desc.name
        if desc.meta.icon:
            self._attr_icon = desc.meta.icon

        low_name = (desc.name or "").lower()
        if any(x in low_name for x in ("error", "alarm", "fault", "Currenterror")):
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        elif any(x in low_name for x in ("pump", "compressor", "running", "StatusCirPump")):
            self._attr_device_class = BinarySensorDeviceClass.RUNNING
        elif "heat" in low_name or "hc" in low_name:
            self._attr_device_class = BinarySensorDeviceClass.HEAT
        elif "cool" in low_name:
            self._attr_device_class = BinarySensorDeviceClass.COLD

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data.get("ebusd", {})
        raw = data.get(self._desc.key)
        if raw is None:
            return None
        return raw.strip().lower() in BINARY_TRUE_VALUES

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
