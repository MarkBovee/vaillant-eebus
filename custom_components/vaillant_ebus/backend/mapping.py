"""Default mapping metadata for all ebusd registers."""

from __future__ import annotations

from .models import RegisterMeta

REGISTER_MAP: dict[str, RegisterMeta] = {
    # hmu (Heat Pump)
    "hmu.Status01": RegisterMeta(
        friendly_name="Status",
        icon="mdi:information",
    ),
    "hmu.Status01.temp": RegisterMeta(
        friendly_name="Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.Status01.pumpstate": RegisterMeta(
        friendly_name="Pump State",
        entity_type="binary_sensor",
    ),
    "hmu.SetMode": RegisterMeta(
        friendly_name="Operation Mode",
        writable=True,
    ),
    "hmu.SetMode.hcmode": RegisterMeta(
        friendly_name="Heating Mode",
        writable=True,
        options=["auto", "day", "night", "off"],
        entity_type="select",
    ),
    "hmu.SetMode.flowtempdesired": RegisterMeta(
        friendly_name="Flow Temperature Target",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=75,
        step=0.5,
        entity_type="number",
    ),
    "hmu.StatusCirPump": RegisterMeta(
        friendly_name="Circulation Pump",
        entity_type="binary_sensor",
    ),
    "hmu.Currenterror": RegisterMeta(
        friendly_name="Error",
        icon="mdi:alert",
    ),
    "hmu.FlowTemp": RegisterMeta(
        friendly_name="Flow Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.FlowTemperature": RegisterMeta(
        friendly_name="Flow Temperature (alt)",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.RunDataCompressorSpeed": RegisterMeta(
        friendly_name="Compressor Speed",
        icon="mdi:speedometer",
        unit="rpm",
    ),
    "hmu.RunDataHighPressure": RegisterMeta(
        friendly_name="High Pressure",
        device_class="pressure",
        unit="bar",
    ),
    "hmu.RunDataLowPressure": RegisterMeta(
        friendly_name="Low Pressure",
        device_class="pressure",
        unit="bar",
    ),
    "hmu.RunDataCompressorInletTemp": RegisterMeta(
        friendly_name="Compressor Inlet Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.RunDataCompressorOutletTemp": RegisterMeta(
        friendly_name="Compressor Outlet Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.RunDataEEVOutletTemp": RegisterMeta(
        friendly_name="EEV Outlet Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.RunDataEEVPositionAbs": RegisterMeta(
        friendly_name="EEV Position",
        icon="mdi:valve",
        unit="%",
    ),
    "hmu.RunDataFan1Speed": RegisterMeta(
        friendly_name="Fan 1 Speed",
        icon="mdi:fan",
        unit="rpm",
    ),
    "hmu.RunDataFan2Speed": RegisterMeta(
        friendly_name="Fan 2 Speed",
        icon="mdi:fan",
        unit="rpm",
    ),
    "hmu.RunDataStatuscode": RegisterMeta(
        friendly_name="Compressor Status",
        icon="mdi:information",
    ),
    "hmu.RunDataAirInletTemp": RegisterMeta(
        friendly_name="Air Inlet Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.RunDataBuildingCPumpPower": RegisterMeta(
        friendly_name="Building Circulation Pump Power",
        device_class="power",
        unit="W",
    ),
    "hmu.CurrentConsumedPower": RegisterMeta(
        friendly_name="Compressor Power",
        device_class="power",
        unit="W",
    ),
    "hmu.CurrentYieldPower": RegisterMeta(
        friendly_name="Thermal Output",
        device_class="power",
        unit="W",
    ),
    "hmu.CurrentCompressorUtil": RegisterMeta(
        friendly_name="Compressor Utilisation",
        icon="mdi:percent",
        unit="%",
    ),
    "hmu.SupplyTempWeighted": RegisterMeta(
        friendly_name="Supply Temperature (weighted)",
        device_class="temperature",
        unit="°C",
    ),
    "hmu.TotalEnergyUsage": RegisterMeta(
        friendly_name="Total Energy",
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
    ),
    "hmu.CopHc": RegisterMeta(
        friendly_name="COP Heating",
        icon="mdi:lightning-bolt",
    ),
    "hmu.CopHwc": RegisterMeta(
        friendly_name="COP DHW",
        icon="mdi:lightning-bolt",
    ),
    "hmu.CopCooling": RegisterMeta(
        friendly_name="COP Cooling",
        icon="mdi:lightning-bolt",
    ),
    "hmu.YieldHc": RegisterMeta(
        friendly_name="Yield Heating",
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
    ),
    "hmu.YieldHcDay": RegisterMeta(
        friendly_name="Yield Heating Today",
        device_class="energy",
        unit="kWh",
    ),
    "hmu.YieldHwc": RegisterMeta(
        friendly_name="Yield DHW",
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
    ),
    "hmu.YieldCoolDay": RegisterMeta(
        friendly_name="Yield Cooling Today",
        device_class="energy",
        unit="kWh",
    ),
    "hmu.RunStatsCompressorHours": RegisterMeta(
        friendly_name="Compressor Runtime",
        device_class="duration",
        unit="h",
        state_class="total_increasing",
        entity_category="diagnostic",
    ),
    "hmu.RunStatsCompressorStarts": RegisterMeta(
        friendly_name="Compressor Starts",
        icon="mdi:counter",
        state_class="total_increasing",
        entity_category="diagnostic",
    ),
    "hmu.RunStatsFan1Hours": RegisterMeta(
        friendly_name="Fan 1 Runtime",
        device_class="duration",
        unit="h",
        state_class="total_increasing",
        entity_category="diagnostic",
    ),
    "hmu.RunStatsFan2Hours": RegisterMeta(
        friendly_name="Fan 2 Runtime",
        device_class="duration",
        unit="h",
        state_class="total_increasing",
        entity_category="diagnostic",
    ),
    "hmu.PowerConsumptionHmu": RegisterMeta(
        friendly_name="Power Consumption (HMU)",
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
    ),
    "hmu.BuildingCircuitFlow": RegisterMeta(
        friendly_name="Building Circuit Flow",
        icon="mdi:water",
        unit="l/min",
    ),
    "hmu.DateTime": RegisterMeta(
        friendly_name="Date/Time",
        icon="mdi:clock",
        entity_category="diagnostic",
    ),
    # ctlv2 (Heating Control)
    "ctlv2.Hc1ActualFlowTempDesired": RegisterMeta(
        friendly_name="Flow Temperature Target (HC1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=75,
        step=0.5,
        entity_type="number",
    ),
    "ctlv2.Hc1PumpStatus": RegisterMeta(
        friendly_name="Pump Status (HC1)",
        entity_type="binary_sensor",
    ),
    "ctlv2.Z1ActualRoomTempDesired": RegisterMeta(
        friendly_name="Room Temperature Target (Z1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=30,
        step=0.5,
        entity_type="number",
    ),
    "ctlv2.Z1DayTemp": RegisterMeta(
        friendly_name="Day Temperature (Z1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=30,
        step=0.5,
        entity_type="number",
    ),
    "ctlv2.Z1NightTemp": RegisterMeta(
        friendly_name="Night Temperature (Z1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=30,
        step=0.5,
        entity_type="number",
    ),
    "ctlv2.Z1OpMode": RegisterMeta(
        friendly_name="Operation Mode (Z1)",
        writable=True,
        options=["day", "night", "auto", "off"],
        entity_type="select",
    ),
    "ctlv2.Hc1FlowTemp": RegisterMeta(
        friendly_name="Flow Temperature (HC1)",
        device_class="temperature",
        unit="°C",
    ),
    "ctlv2.Hc1HeatCurve": RegisterMeta(
        friendly_name="Heat Curve (HC1)",
        writable=True,
        min_value=0.1,
        max_value=4.0,
        step=0.05,
        entity_type="number",
    ),
    "ctlv2.Hc1MaxFlowTempDesired": RegisterMeta(
        friendly_name="Max Flow Temperature (HC1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=20,
        max_value=75,
        step=1,
        entity_type="number",
    ),
    "ctlv2.Hc1MinFlowTempDesired": RegisterMeta(
        friendly_name="Min Flow Temperature (HC1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=5,
        max_value=40,
        step=1,
        entity_type="number",
    ),
    "ctlv2.Hc1SummerTempLimit": RegisterMeta(
        friendly_name="Summer Temp Limit (HC1)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=10,
        max_value=30,
        step=1,
        entity_type="number",
    ),
    "ctlv2.Hc1RoomTempSwitchOn": RegisterMeta(
        friendly_name="Room Temp Switch On (HC1)",
        device_class="temperature",
        unit="°C",
    ),
    "ctlv2.Hc1Status": RegisterMeta(
        friendly_name="Status (HC1)",
        icon="mdi:information",
    ),
    "ctlv2.Hc1CircuitType": RegisterMeta(
        friendly_name="Circuit Type (HC1)",
        icon="mdi:information",
        entity_category="diagnostic",
    ),
    "ctlv2.HwcTempDesired": RegisterMeta(
        friendly_name="DHW Target Temperature",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=30,
        max_value=70,
        step=1,
        entity_type="number",
    ),
    "ctlv2.HwcStorageTemp": RegisterMeta(
        friendly_name="DHW Storage Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "ctlv2.HwcOpMode": RegisterMeta(
        friendly_name="DHW Operation Mode",
        writable=True,
        options=["off", "on", "auto"],
        entity_type="select",
    ),
    "ctlv2.HwcMaxFlowTempDesired": RegisterMeta(
        friendly_name="Max Flow Temperature (DHW)",
        device_class="temperature",
        unit="°C",
        writable=True,
        min_value=20,
        max_value=75,
        step=1,
        entity_type="number",
    ),
    "ctlv2.WaterPressure": RegisterMeta(
        friendly_name="Water Pressure",
        device_class="pressure",
        unit="bar",
    ),
    "ctlv2.Currenterror": RegisterMeta(
        friendly_name="Error",
        icon="mdi:alert",
    ),
    "ctlv2.AdaptHeatCurve": RegisterMeta(
        friendly_name="Adapt Heat Curve",
        writable=True,
        options=["no", "yes"],
        entity_type="select",
    ),
    "ctlv2.SystemFlowTemp": RegisterMeta(
        friendly_name="System Flow Temperature",
        device_class="temperature",
        unit="°C",
    ),
    # Broadcast (System)
    "Broadcast.Outsidetemp": RegisterMeta(
        friendly_name="Outside Temperature",
        device_class="temperature",
        unit="°C",
    ),
    "Broadcast.Vdatetime": RegisterMeta(
        friendly_name="Date/Time",
        icon="mdi:clock",
        entity_category="diagnostic",
    ),
    "Broadcast.Vdatetime.time": RegisterMeta(
        friendly_name="Time",
        icon="mdi:clock",
        entity_category="diagnostic",
    ),
    "Broadcast.Vdatetime.date": RegisterMeta(
        friendly_name="Date",
        icon="mdi:calendar",
        entity_category="diagnostic",
    ),
    "Broadcast.Datetime": RegisterMeta(
        friendly_name="Date/Time",
        icon="mdi:clock",
        entity_category="diagnostic",
    ),
    "Broadcast.Error": RegisterMeta(
        friendly_name="System Error",
        icon="mdi:alert",
        entity_category="diagnostic",
    ),
    # vwz (Valve)
    "vwz.TestHwcTemp": RegisterMeta(
        friendly_name="DHW Temperature (test)",
        device_class="temperature",
        unit="°C",
        entity_category="diagnostic",
    ),
    "vwz.TestOutdoorTemp": RegisterMeta(
        friendly_name="Outdoor Temperature (test)",
        device_class="temperature",
        unit="°C",
        entity_category="diagnostic",
    ),
    "vwz.TestThreeWayValve": RegisterMeta(
        friendly_name="Three-Way Valve (test)",
        entity_category="diagnostic",
    ),
    # global (ebusd daemon) — diagnostic only
    "global.running": RegisterMeta(
        friendly_name="ebusd Running",
        entity_type="binary_sensor",
        entity_category="diagnostic",
    ),
    "global.signal": RegisterMeta(
        friendly_name="ebusd Signal",
        entity_type="binary_sensor",
        entity_category="diagnostic",
    ),
    "global.scan": RegisterMeta(
        friendly_name="ebusd Scan Status",
        entity_category="diagnostic",
    ),
    "global.uptime": RegisterMeta(
        friendly_name="ebusd Uptime",
        entity_category="diagnostic",
    ),
    "global.version": RegisterMeta(
        friendly_name="ebusd Version",
        entity_category="diagnostic",
    ),
}


def get_meta(circuit: str, name: str, field: str = "value") -> RegisterMeta:
    key = f"{circuit}.{name}"
    if field != "value":
        key += f".{field}"
    return REGISTER_MAP.get(key, RegisterMeta())
