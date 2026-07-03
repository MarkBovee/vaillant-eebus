"""Select platform for Vaillant EEBUS HVAC mode control."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VaillantCoordinator

HVAC_MODES = ["heating", "cooling", "ventilation", "standby", "auto"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]
    servers = coordinator.client.all_server_features.get("HVAC", [])
    room_server = next((s for s in servers if s.get("entity") == [5, 1, 1]), None)
    if room_server is not None:
        async_add_entities([VaillantHvacModeSelect(coordinator, room_server, entry)])


class VaillantHvacModeSelect(CoordinatorEntity[VaillantCoordinator], SelectEntity):
    """Select entity for HVAC operating mode."""

    def __init__(
        self,
        coordinator: VaillantCoordinator,
        server: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._server = server
        self._attr_unique_id = f"{entry.entry_id}_hvac_mode"
        self._attr_name = "HVAC Mode"
        self._attr_has_entity_name = True
        self._attr_device_info = coordinator.device_info
        self._attr_options = HVAC_MODES

    @property
    def current_option(self) -> str | None:
        return None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.write_hvac_mode(self._server, option)
