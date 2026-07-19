"""Entity factory — generate HA entities from discovered ebusd registers."""

from __future__ import annotations

from typing import Any

from .mapping import RegisterMeta, get_meta
from .models import EbusdRegister


def _is_hidden_register(register: EbusdRegister) -> bool:
    """Exclude ebusd implementation/config noise from entity creation."""
    circuit = register.circuit.lower()
    name = register.name.lower()
    if circuit.startswith("scan"):
        return True
    if circuit == "broadcast" and name != "outsidetemp":
        return True
    if name.startswith(("cctimer_", "hwctimer_", "z1timer_", "z2timer_", "z3timer_")):
        return True
    if name.startswith(("memory_", "prfuelsum", "installer", "phonenumber")):
        return True
    if name in {"general_valuerange", "date_time", "datetime", "vdatetime"}:
        return True
    return False


class EntityDescription:
    def __init__(
        self,
        circuit: str,
        name: str,
        field: str,
        meta: RegisterMeta,
        register: EbusdRegister,
        raw_value: str | None = None,
    ) -> None:
        self.circuit = circuit
        self.name = name
        self.field = field
        self.meta = meta
        self.register = register
        self.raw_value = raw_value or ""

    @property
    def unique_id(self) -> str:
        suffix = self.name.lower().replace(" ", "_")
        if self.field != "value":
            suffix += f"_{self.field}"
        return f"ebusd_{self.circuit}_{suffix}"

    @property
    def key(self) -> str:
        return f"{self.circuit}.{self.name}.{self.field}"

    @property
    def entity_type(self) -> str:
        return self.meta.entity_type or ("binary_sensor" if self._is_binary else "sensor")

    @property
    def _is_binary(self) -> bool:
        low = self.raw_value.lower().strip() if self.raw_value else ""
        return low in ("on", "off", "true", "false", "1", "0", "yes", "no")


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _classify_register(
    register: EbusdRegister, field: str, raw_value: str | None
) -> str:
    meta = get_meta(register.circuit, register.name, field)
    if meta.entity_type:
        return meta.entity_type

    if raw_value is None or raw_value == "" or raw_value == "-":
        return "sensor"

    low = raw_value.strip().lower()
    if low in ("on", "off", "true", "false"):
        return "binary_sensor" if not register.writable else "switch"
    if low in ("0", "1", "yes", "no"):
        if register.writable:
            return "switch"
        return "binary_sensor"
    if not _is_numeric(raw_value) and ";" not in raw_value:
        pass

    if register.writable and _is_numeric(raw_value):
        meta_min = meta.min_value
        meta_max = meta.max_value
        if meta_min is not None and meta_max is not None:
            return "number"

    return "sensor"


def generate_entity_descriptions(
    registers: list[EbusdRegister],
    yaml_overrides: dict[str, dict[str, Any]] | None = None,
) -> list[EntityDescription]:
    overrides = yaml_overrides or {}
    seen: set[str] = set()
    entities: list[EntityDescription] = []

    for reg in registers:
        if _is_hidden_register(reg):
            continue

        for field in reg.fields:
            raw = reg.value.get(field)
            key = f"{reg.circuit}.{reg.name}.{field}"
            entity_key = f"{reg.circuit}.{reg.name}"
            if field == "value":
                entity_key = key

            if entity_key in seen:
                continue
            seen.add(entity_key)

            meta = get_meta(reg.circuit, reg.name, field)
            override = overrides.get(f"{reg.circuit}.{reg.name}") or {}
            override = overrides.get(key) or override

            merged_meta = _merge_overrides(meta, override)

            if merged_meta.entity_type == "":
                merged_meta.entity_type = _classify_register(reg, field, raw)

            if not reg.has_data and not merged_meta.entity_category:
                merged_meta.enabled = False

            if not merged_meta.enabled:
                continue

            entity = EntityDescription(
                circuit=reg.circuit,
                name=reg.name,
                field=field,
                meta=merged_meta,
                register=reg,
                raw_value=raw,
            )
            entities.append(entity)

    return entities


def _merge_overrides(meta: RegisterMeta, override: dict[str, Any]) -> RegisterMeta:
    if not override:
        return meta
    merged = RegisterMeta(
        friendly_name=override.get("friendly_name", meta.friendly_name),
        icon=override.get("icon", meta.icon),
        unit=override.get("unit", meta.unit),
        device_class=override.get("device_class", meta.device_class),
        state_class=override.get("state_class", meta.state_class),
        entity_category=override.get("entity_category", meta.entity_category),
        writable=override.get("writable", meta.writable),
        min_value=override.get("min", meta.min_value),
        max_value=override.get("max", meta.max_value),
        step=override.get("step", meta.step),
        options=override.get("options", meta.options),
        enabled=override.get("enabled", meta.enabled),
        entity_type=override.get("entity_type", meta.entity_type),
    )
    return merged
