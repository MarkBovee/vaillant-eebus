# Measurement Reading

## Scope

Discover and read measurement data from VR921 entities.

## Requirements

### R1: Entity discovery
Request `nodeManagementDetailedDiscoveryData` from VR921. Parse entity tree (DeviceInformation, HeatPumpAppliance, Compressor, DHWCircuit, HeatingZone, TemperatureSensor).

### R2: Measurement server identification
Find features with `featureType=11` (Measurement server) per entity.

### R3: Description
`measurementDescriptionListData` — parse scopeType, unit, measurementId per server.

### R4: Read
`measurementListData` — read current values from each measurement server.

### R5: Subscribe
`NodeManagementSubscriptionRequestCall` — subscribe to measurement updates. Receive notify datagrams with new values.

### R6: Entity mapping
Map VR921 entities to HA sensor entities:
- Entity [3,1] → Compressor (power, energy)
- Entity [4] → DHW Circuit (temperature)
- Entity [5,1,1] → HVAC Room (temperature)
- Entity [6] → Temperature Sensor (outdoor)
