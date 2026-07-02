"""Constants for Vaillant EEBUS."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "vaillant_eebus"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_PORT = 12480
DEFAULT_SCAN_INTERVAL = 60
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]
