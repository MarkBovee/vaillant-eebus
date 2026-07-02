# Tasks: Vaillant EEBUS Integration — Phase 1 (Read-Only)

## Milestone 1: Repository scaffolding

- [ ] Initialize Python project (`pyproject.toml`, `requirements.txt`, `requirements_test.txt`)
- [ ] Create `hacs.json` with domain `vaillant_eebus`
- [ ] Create `custom_components/vaillant_eebus/manifest.json` (domain, version, deps)
- [ ] Create `LICENSE` (Apache 2.0)
- [ ] Create `README.md` with badges, install instructions, feature overview
- [ ] Set up CI: Ruff, mypy, pytest, coverage, HACS validation
- [ ] Set up `pre-commit-config.yaml`
- [ ] Initialize test structure (`tests/conftest.py`, `tests/__init__.py`)

## Milestone 2: Protocol — SHIP/SPINE transport

- [ ] Evaluate `ULudo/eebus-sdk` against VR921 (or use mock)
  - If works: add as PyPI dependency
  - If not: decide on fork or custom impl
- [ ] Implement `vaillant/certificate.py` — self-signed X.509 cert generation, SKI extraction
- [ ] Implement `vaillant/discovery.py` — mDNS listener for `_ship._tcp.local.`, VR921 candidate tracking
- [ ] Implement SHIP connection: TLS WebSocket, handshake state machine
- [ ] Implement SPINE datagram read/write (if not in SDK)
- [ ] Implement reconnect with exponential backoff
- [ ] Unit tests for certificate generation
- [ ] Unit tests for discovery parsing
- [ ] Unit tests for handshake (mock server)

## Milestone 3: Protocol — VR921 measurement reading

- [ ] Implement VR921 entity tree discovery (nodeManagementDetailedDiscoveryData)
- [ ] Identify Measurement server features per entity
- [ ] Implement subscription (NodeManagementSubscriptionRequestCall)
- [ ] Implement measurement parsing (measurementDescriptionListData + measurementListData)
- [ ] Map SPINE measurement IDs to HA-friendly names + units
- [ ] Implement poll fallback for non-subscribable measurements
- [ ] Unit tests with mock VR921 server
- [ ] Integration test: full discovery → subscribe → read cycle

## Milestone 4: HA Integration — Setup

- [ ] Implement `__init__.py` — async_setup_entry, async_unload_entry
- [ ] Implement `const.py` — DOMAIN, platform lists, defaults
- [ ] Implement `config_flow.py`:
  - [ ] mDNS discovery step
  - [ ] Manual IP fallback step
  - [ ] Connection test step
  - [ ] Options flow (update interval)
- [ ] Implement `coordinator.py`:
  - [ ] DataUpdateCoordinator wrapping VR921 client
  - [ ] Heartbeat + reconnect
  - [ ] State management (online/offline)
  - [ ] CoordinatorEntity base class
- [ ] Implement `device.py` — DeviceInfo from VR921 discovery data
- [ ] Test config flow with mock
- [ ] Test coordinator reconnect
- [ ] Test coordinator entity lifecycle

## Milestone 5: HA Integration — Entities

- [ ] Implement `sensor.py`:
  - [ ] Outdoor temperature
  - [ ] Flow temperature
  - [ ] Return temperature
  - [ ] DHW tank temperature
  - [ ] Room temperature
  - [ ] Heating curve
  - [ ] Compressor frequency
  - [ ] Compressor runtime
  - [ ] Power consumption
  - [ ] Thermal output
  - [ ] COP
  - [ ] Energy today / total
  - [ ] Water pressure
  - [ ] Error code
  - [ ] Firmware version
- [ ] Implement `binary_sensor.py`:
  - [ ] Compressor running
  - [ ] Heating active
  - [ ] Cooling active
  - [ ] Defrost active
  - [ ] Hot water active
  - [ ] Alarm
  - [ ] Internet connected
- [ ] Implement `diagnostics.py`:
  - [ ] Full data dump
  - [ ] Redact sensitive info (certs, SKI, IPs)
- [ ] Implement `strings.json` + `translations/` (English)
- [ ] Entity tests for each sensor type
- [ ] Snapshot test for diagnostics output

## Milestone 6: Polish

- [ ] Create `docs/architecture.md` with C4 diagram
- [ ] Create `docs/developer.md` — setup, testing, contributing
- [ ] Create `docs/troubleshooting.md` — common issues
- [ ] Create `docs/faq.md`
- [ ] Create `examples/basic_dashboard.yaml`
- [ ] Full Ruff compliance pass
- [ ] Full mypy strict pass
- [ ] Coverage report — target 90%+
- [ ] Final README polish
- [ ] Tag v0.1.0 release

## Out of scope (Phase 2+)

- Subscriptions → real-time updates
- Climate platform → target temperature, quick veto
- Number platform → flow temperature, max compressor power
- Switch platform → hot water boost, holiday mode
- Select platform → operating modes
- Services → set_quick_veto, set_holiday, etc.
- Energy dashboard integration
