# Vaillant EEBUS

Local Home Assistant integration for Vaillant heat pumps via the VR921 (sensoNET) EEBUS interface.

**No cloud dependency. No addon. No extra hardware.**

## Features

- Read heat pump data directly from VR921 over local network
- mDNS discovery — no IP configuration needed
- 25+ sensor entities (temperatures, power, energy, COP, pressure, etc.)
- Binary sensors (compressor, alarm, defrost, etc.)
- Async from day one
- Diagnostics support
- HACS installable

## Architecture

```
VR921 ──wss://──► vaillant/ ──► custom_components/ ──► HA entities
        SHIP/SPINE   ship/spine       vaillant_eebus      sensors
```

## Requirements

- Vaillant heat pump with VR921 (sensoNET) gateway
- Home Assistant 2025.x or newer
- Network access to VR921 (mDNS must work)
- Python 3.14+

## Installation

### HACS

1. Add this repository as a custom repository in HACS
2. Search for "Vaillant EEBUS" and install
3. Restart Home Assistant
4. Settings → Devices & Services → Add Integration → Vaillant EEBUS

### Manual

1. Download latest release
2. Extract `custom_components/vaillant_eebus` to your HA `config/custom_components/`
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## First-time pairing

1. Install and add the integration
2. The integration will discover your VR921 via mDNS
3. Confirm the pairing request in the myVaillant app
4. Done — data appears automatically

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pytest
```

## License

Apache 2.0
