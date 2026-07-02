# HA Integration

## Scope

Home Assistant custom component wrapping the vaillant/ library.

## Requirements

### R1: ConfigFlow
mDNS discovery step + manual IP fallback + connection test.

### R2: DataUpdateCoordinator
Holds SHIP WebSocket connection. Manages reconnect with backoff. Heartbeat.

### R3: Entities
SensorEntity (temperature, power, energy) and BinarySensorEntity (compressor running, alarm).

### R4: unique_id
Deterministic from VR921 SKI + entity + feature + measurement ID.

### R5: Diagnostics
Full data dump from VR921. Redact certs, SKI, IPs.

### R6: HACS
`hacs.json` with domain `vaillant_eebus`. Zipped release.
