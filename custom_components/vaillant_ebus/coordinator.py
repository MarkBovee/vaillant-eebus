"""Coordinator for Vaillant eBUS."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .backend.entity_factory import EntityDescription, generate_entity_descriptions
from .backend.models import CIRCUIT_NAMES, EbusdRegister
from .backend.tcp import EbusdTcpBackend
from .const import (
    CONF_EBUSD_HOST,
    CONF_EBUSD_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_EBUSD_POLL_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class VaillantCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        _LOGGER.info("Initializing coordinator")
        self._entry = entry

        self.ebusd_backend: EbusdTcpBackend | None = None
        self.registers: dict[str, EbusdRegister] = {}
        self.entities: list[EntityDescription] = []
        self._started = False
        self._poll_registers: list[tuple[str, str, str]] = []

        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_EBUSD_POLL_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def async_start(self) -> None:
        if self._started:
            return
        self._started = True
        host = self._entry.data.get(CONF_EBUSD_HOST)
        port = self._entry.data.get(CONF_EBUSD_PORT, 8888)
        if not host:
            raise UpdateFailed("Missing ebusd host")
        _LOGGER.info("Starting ebusd backend to %s:%s", host, port)
        self.ebusd_backend = EbusdTcpBackend(host=host, port=port)
        await self.ebusd_backend.async_connect()

        discovered = await self.ebusd_backend.async_find()
        for reg in discovered:
            self.registers[reg.key] = reg
        _LOGGER.info("Discovered %d ebusd registers", len(discovered))

        self.entities = generate_entity_descriptions(discovered)

        for reg in discovered:
            if reg.has_data:
                for field in reg.fields:
                    self._poll_registers.append((reg.circuit, reg.name, field))
        _LOGGER.info("Poll list: %d register fields", len(self._poll_registers))

    async def _async_update_data(self) -> dict[str, Any]:
        _LOGGER.debug("Coordinator update, started=%s", self._started)
        if not self._started:
            await self.async_start()

        if self.ebusd_backend and self.ebusd_backend.connected:
            try:
                polled = await self.ebusd_backend.async_poll(self._poll_registers)
                return {"ebusd": polled}
            except ConnectionError:
                _LOGGER.warning("ebusd connection lost, reconnecting")
                try:
                    await self.ebusd_backend.async_reconnect()
                except Exception as exc:
                    _LOGGER.error("ebusd reconnect failed: %s", exc)

        return {}

    async def async_stop(self) -> None:
        if self.ebusd_backend:
            await self.ebusd_backend.async_disconnect()

    def get_device_info(self, circuit: str) -> DeviceInfo:
        name = CIRCUIT_NAMES.get(circuit, f"Vaillant ({circuit})")
        return DeviceInfo(
            identifiers={(DOMAIN, circuit)},
            name=name,
            manufacturer="Vaillant",
            model=name,
            sw_version=self.ebusd_backend.version if self.ebusd_backend else None,
        )
