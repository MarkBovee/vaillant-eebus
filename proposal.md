# Proposal: Vaillant EEBUS Local Integration

## What

A production-grade Home Assistant **custom integration** (HACS) for Vaillant heat pumps using the local EEBUS interface on the VR921 (sensoNET) gateway. Read-only in Phase 1, write support in later phases.

No cloud dependency. No addon/bridge container.

## Why

Existing options:

| Approach | Problem |
|----------|---------|
| `mypyllant-component` (cloud API) | Quota limits, API incidents, internet required, lag |
| `ebusd` + hardware adapter | Extra hardware, eBUS (different protocol), serial |
| `CoreTex/homeassistant-eebus` (Go addon) | HAOS-only, 2 components to maintain, overkill |

A pure Python EEBUS integration solves all of these: local, low-latency, no extra infra, works on all HA install types.

## How

### Architecture

```
┌──────────┐  EEBUS/SHIP    ┌──────────────────┐
│ VR921    │◄────wss:──────►│  eebus-sdk        │  ← SHIP/SPINE transport
│ Gateway  │   mDNS/_ship   │  (ULudo)          │     mDNS, TLS, certs
└──────────┘                └────────┬─────────┘
                                     │
                            ┌────────▼─────────┐
                            │  vaillant-eebus   │  ← Vaillant-specific
                            │  vaillant/        │     entity/feature discovery
                            │                   │     measurement parsing
                            └────────┬─────────┘
                                     │
                            ┌────────▼─────────┐
                            │  custom_components│  ← HA integration
                            │  /vaillant_eebus/ │     DataUpdateCoordinator
                            │                   │     CoordinatorEntity
                            │                   │     ConfigFlow, platforms
                            └──────────────────┘
```

### Existing projects to build on

| Project | Role |
|---------|------|
| **ULudo/eebus-sdk** (Python, Apache 2.0) | Core SHIP/SPINE transport — mDNS, TLS WebSocket, HemsClient |
| **markusschultheis/Vaillant-VR921** (Python, no license) | Reference for VR921 entity/feature structure, SPINE datagram format |

### Dependency strategy

**Primary:** PyPI dependency on `ULudo/eebus-sdk` for SHIP/SPINE.
**Fallback:** Fork/extend SDK if VR921 private use cases aren't covered.
**Last resort:** Ship own SHIP/SPINE implementation (based on markusschultheis reference).

### Key decisions

- **Pure integration, no addon** — Docker container adds complexity with zero benefit here
- **3-layer separation** — protocol (`eebus-sdk`), Vaillant domain (`vaillant/`), HA (`custom_components/`)
- **Async from day 1** — HA requires it, EEBUS is inherently async
- **ConfigFlow with mDNS discovery** — automatic VR921 detection, fallback to manual IP
- **DataUpdateCoordinator** — standard HA pattern for polling + subscriptions
- **SHIP identity/certificate** — generated once, reused for stable SKI
- **Pairing via myVaillant app** — first connect requires trust confirmation, then certificate-based

### Scope

**Phase 1 (this change):** Read-only integration
- mDNS discovery + config flow
- Connect to VR921 via SHIP/SPINE
- Read all measurement entities (temperatures, power, energy, status)
- Binary sensors (compressor running, alarm, etc.)
- Device info + diagnostics
- Tests at >90% coverage
- CI (Ruff, mypy, pytest, pre-commit)
- Documentation (README, architecture, troubleshooting)

**Not in scope (later phases):**
- Write operations (climate, switch, number)
- Subscriptions (event-based updates)
- Energy dashboard
- Advanced automation support
