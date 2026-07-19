"""Switch platform for Vaillant EEBUS."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VaillantCoordinator

SWITCH_ON_VALUES = {"1", "on", "true", "yes"}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = []

    for desc in coordinator.entities:
        if desc.entity_type != "switch":
            continue
        uid = f"{entry.entry_id}_{desc.unique_id}"
        entities.append(EbusdSwitch(coordinator, desc, uid, entry))

    async_add_entities(entities)


class EbusdSwitch(CoordinatorEntity[VaillantCoordinator], SwitchEntity):
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

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data.get("ebusd", {})
        raw = data.get(self._desc.key)
        if raw is None:
            return None
        return raw.strip().lower() in SWITCH_ON_VALUES

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write("1")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write("0")

    async def _write(self, value: str) -> None:
        if self.coordinator.ebusd_backend:
            result = await self.coordinator.ebusd_backend.async_write(
                self._desc.circuit,
                self._desc.name,
                value,
            )
            if result.success:
                await self.coordinator.async_request_refresh()
