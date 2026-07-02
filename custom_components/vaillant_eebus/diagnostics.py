"""Diagnostics support for Vaillant EEBUS."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import VaillantCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: VaillantCoordinator = hass.data[DOMAIN][entry.entry_id]

    measurements = dict(coordinator.client.latest_measurements)
    for key, val in measurements.items():
        if isinstance(val, dict) and "value" in val:
            val["value"] = str(val["value"])

    return {
        "entry_data": dict(entry.data),
        "device_info": dict(coordinator.client.device_info),
        "connected": coordinator.client.connected,
        "latest_measurements": measurements,
    }
