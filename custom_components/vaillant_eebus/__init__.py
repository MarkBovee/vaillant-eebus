"""Vaillant EEBUS integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from vaillant.certificate import get_or_create_certificate

from .const import DOMAIN, PLATFORMS
from .coordinator import VaillantCoordinator

_LOGGER = logging.getLogger(__name__)


async def _handle_set_dhw_temperature(call: ServiceCall, coordinator: VaillantCoordinator) -> None:
    temperature = call.data["temperature"]
    servers = coordinator.client.setpoint_servers
    dhw_server = next((s for s in servers if s.get("entity") == [4]), None)
    if dhw_server is None:
        _LOGGER.warning("No DHW setpoint server found")
        return
    await coordinator.client.write_setpoint(dhw_server, temperature)


async def _handle_set_hvac_mode(call: ServiceCall, coordinator: VaillantCoordinator) -> None:
    mode = call.data["mode"]
    servers = coordinator.client.all_server_features.get("HVAC", [])
    room_server = next((s for s in servers if s.get("entity") == [5, 1, 1]), None)
    if room_server is None:
        _LOGGER.warning("No HVAC server found")
        return
    await coordinator.client.write_hvac_mode(room_server, mode)


SET_DHW_SCHEMA = vol.Schema({vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=5, max=80))})
SET_HVAC_SCHEMA = vol.Schema({vol.Required("mode"): vol.In(["heating", "cooling", "ventilation", "standby", "auto"])})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    logging.getLogger("vaillant").setLevel(logging.INFO)
    logging.getLogger("custom_components.vaillant_eebus").setLevel(logging.DEBUG)
    _LOGGER.info("Setting up vaillant_eebus entry: %s", entry.data)
    hass.data.setdefault(DOMAIN, {})
    try:
        cert_ski = await hass.async_add_executor_job(get_or_create_certificate)
        _LOGGER.info("Certificate loaded, SKI=%s", cert_ski[:16])
    except Exception as exc:
        _LOGGER.error("Failed to load certificate: %s", exc, exc_info=True)
        return False
    try:
        coordinator = VaillantCoordinator(hass, entry, cert_ski)
        hass.data[DOMAIN][entry.entry_id] = coordinator
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info("Coordinator first refresh OK")
    except Exception as exc:
        _LOGGER.error("Coordinator setup failed: %s", exc, exc_info=True)
        return False
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def svc_set_dhw(call: ServiceCall) -> None:
        await _handle_set_dhw_temperature(call, coordinator)

    async def svc_set_hvac(call: ServiceCall) -> None:
        await _handle_set_hvac_mode(call, coordinator)

    hass.services.async_register(DOMAIN, "set_dhw_target_temperature", svc_set_dhw, schema=SET_DHW_SCHEMA)
    hass.services.async_register(DOMAIN, "set_hvac_mode", svc_set_hvac, schema=SET_HVAC_SCHEMA)
    _LOGGER.info("vaillant_eebus setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, "set_dhw_target_temperature")
    hass.services.async_remove(DOMAIN, "set_hvac_mode")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.stop()
    return True
