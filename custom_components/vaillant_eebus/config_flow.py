"""Config flow for Vaillant EEBUS."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class VaillantConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vaillant EEBUS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Vaillant EEBUS (VR921)",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOST, default=""): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): int,
                }
            ),
        )

    async def async_step_zeroconf(
        self, discovery_info: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        return await self.async_step_user()

    async def async_step_dhcp(
        self, discovery_info: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle DHCP discovery."""
        return await self.async_step_user()
