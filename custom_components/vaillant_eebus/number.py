"""Number platform for Vaillant EEBUS writable setpoints."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity
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
    servers = coordinator.client.setpoint_servers
    dhw_server = next((s for s in servers if s.get("entity") == [4]), None)
    if dhw_server is not None:
        async_add_entities([VaillantDhwSetpointNumber(coordinator, dhw_server, entry)])


class VaillantDhwSetpointNumber(CoordinatorEntity[VaillantCoordinator], NumberEntity):
    """Number entity for DHW target temperature."""

    def __init__(
        self,
        coordinator: VaillantCoordinator,
        server: dict[str, Any],
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._server = server
        self._attr_unique_id = f"{entry.entry_id}_dhw_setpoint"
        self._attr_name = "DHW Target Temperature"
        self._attr_has_entity_name = True
        self._attr_device_info = coordinator.device_info
        self._attr_native_min_value = 35.0
        self._attr_native_max_value = 65.0
        self._attr_native_step = 1.0
        self._attr_native_unit_of_measurement = "°C"

    @property
    def native_value(self) -> float | None:
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.write_setpoint(self._server, value)
