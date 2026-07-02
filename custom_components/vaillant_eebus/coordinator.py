"""Coordinator for Vaillant EEBUS."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from vaillant.client import VaillantClient

from .const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class VaillantCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator for Vaillant EEBUS data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.client = VaillantClient(
            measurement_callback=self._async_heartbeat_callback
        )
        self._host = entry.data.get(CONF_HOST)
        self._port = entry.data.get(CONF_PORT, DEFAULT_PORT)
        self._entry = entry

        update_interval = timedelta(
            seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_heartbeat_callback(
        self, measurements: dict[str, dict[str, Any]]
    ) -> None:
        self.async_set_updated_data(dict(measurements))

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        if self.client.latest_measurements:
            return dict(self.client.latest_measurements)
        raise UpdateFailed("No measurements yet")

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._host or "vaillant_eebus")},
            name="Vaillant EEBUS (VR921)",
            manufacturer="Vaillant",
            model="VR921",
        )
