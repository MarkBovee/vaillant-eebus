"""VaillantClient — EEBUS SHIP/SPINE client for Vaillant VR921."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import socket
import ssl
import time
from typing import Any, cast

from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

from . import const
from .certificate import get_or_create_certificate
from .discovery import (
    MDNSHandler,
    _entity_addr_list,
    _extract_entities,
    _extract_measurement_servers,
    _extract_remote_landmap,
    _is_prefix,
    handle_spine_read,
    request_remote_detailed_discovery,
    request_remote_node_management_use_case_data,
)
from .measurement import (
    parse_measurement_description,
    parse_measurement_list,
    request_remote_measurement_once,
    subscribe_remote_measurement,
)
from .ship import (
    MsgCounter,
    _parse_spine_datagram,
    json_from_eebus_json,
    json_into_eebus_json,
    perform_ship_handshake,
    send_ship_json,
)
from .spine import send_spine_result_ok

_LOGGER = logging.getLogger(__name__)


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unknown"


def _unit_to_ha(unit: Any) -> str:
    if unit is None:
        return ""
    if isinstance(unit, str):
        u = unit.strip()
        if u == "degC":
            return "°C"
        if u == "degF":
            return "°F"
        return u
    if isinstance(unit, dict):
        u = unit.get("unit") or unit.get("name")
        return _unit_to_ha(str(u)) if u is not None else ""
    return str(unit)


def _guess_ha_metadata(scope_type: str, unit: str) -> dict[str, str]:
    s = (scope_type or "").lower()
    u = (unit or "").strip()
    if "temperature" in s:
        return {"device_class": "temperature", "state_class": "measurement", "unit": u or "°C"}
    if "power" in s:
        return {"device_class": "power", "state_class": "measurement", "unit": u or "W"}
    if "energy" in s:
        return {"device_class": "energy", "state_class": "total_increasing", "unit": u or "Wh"}
    if "current" in s:
        return {"device_class": "current", "state_class": "measurement", "unit": u or "A"}
    if "voltage" in s:
        return {"device_class": "voltage", "state_class": "measurement", "unit": u or "V"}
    return {"device_class": "", "state_class": "measurement", "unit": u}


def _friendly_sensor_name(scope_type: str, *, source_entity: list[int] | None = None) -> str:
    s = (scope_type or "").strip()
    low = s.lower()
    if low == "outsideairtemperature":
        return "Outside Temperature"
    if low == "dhwtemperature":
        return "DHW Temperature"
    if low == "roomairtemperature":
        return "Room Temperature"
    if low == "acpowertotal":
        return "Compressor Power"
    if low.startswith("acpower"):
        return "Power"
    if "temperature" in low:
        return "Temperature"
    if source_entity:
        return f"{s} (entity={source_entity})"
    return s or "Measurement"


class VaillantClient:
    """Manage one EEBUS SHIP/SPINE connection to a Vaillant VR921.

    Call run() to start the full lifecycle. Measurements arrive via the
    callback or are readable via latest_measurements.
    """

    def __init__(
        self,
        *,
        measurement_callback: Any | None = None,
        spine_message_callback: Any | None = None,
        publish_jsonl: bool = False,
    ):
        self._cert_ski = get_or_create_certificate()
        self._msg_counter = MsgCounter()
        self._local_ship_id = f"ha-vaillant-eebus-{self._cert_ski[:12]}"
        self._local_device_address = f"d:_i:1_{self._local_ship_id}"
        self._measurement_callback = measurement_callback
        self._spine_message_callback = spine_message_callback
        self._publish_jsonl = publish_jsonl

        self._ws: Any = None
        self._aiozc: AsyncZeroconf | None = None
        self._task: asyncio.Task | None = None

        self._latest_measurements: dict[str, dict[str, Any]] = {}
        self._device_info: dict[str, Any] = {}
        self._remote_entities: list[dict[str, Any]] = []
        self._remote_measurement_servers: list[dict[str, Any]] = []
        self._measurement_desc_maps: dict[tuple[tuple[int, ...], int], dict[int, dict[str, Any]]] = {}

        self._running = False

    @property
    def latest_measurements(self) -> dict[str, dict[str, Any]]:
        return dict(self._latest_measurements)

    @property
    def device_info(self) -> dict[str, Any]:
        return dict(self._device_info)

    @property
    def measurement_descriptions(self) -> list[dict[str, Any]]:
        descriptions: list[dict[str, Any]] = []
        for (entity, feature), desc_map in sorted(self._measurement_desc_maps.items()):
            for measurement_id, meta in sorted(desc_map.items()):
                descriptions.append(
                    {
                        "entity": list(entity),
                        "feature": feature,
                        "measurementId": measurement_id,
                        **meta,
                    }
                )
        return descriptions

    @property
    def connected(self) -> bool:
        return self._running and self._ws is not None

    async def discover_target(self, *, timeout: int = 30) -> dict[str, Any] | None:
        """Discover VR921 via mDNS. Returns target dict or None."""
        aiozc = AsyncZeroconf(ip_version=IPVersion.V4Only)
        handler = MDNSHandler(self._cert_ski)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        desc = {"txtvers": "1", "path": "/ship/", "ski": self._cert_ski, "register": "true"}
        info = AsyncServiceInfo(
            const.SHIP_SERVICE_TYPE,
            f"HomeAssistant-Vaillant-EEBUS.{const.SHIP_SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=54885,
            properties=desc,
        )
        await aiozc.async_register_service(info)
        AsyncServiceBrowser(aiozc.zeroconf, const.SHIP_SERVICE_TYPE, handler)

        elapsed = 0
        while handler.target_info is None and elapsed < timeout:
            await asyncio.sleep(1)
            elapsed += 1

        await aiozc.async_unregister_all_services()
        await aiozc.async_close()

        if handler.target_info is None:
            return None

        target_ip = socket.inet_ntoa(handler.target_info.addresses[0])
        target_port = handler.target_info.port
        target_ski = handler.target_info.properties.get(b"ski", b"unknown").decode("utf-8")

        return {"host": target_ip, "port": target_port, "ski": target_ski, "local_ip": local_ip}

    async def connect_and_subscribe(
        self, host: str, port: int, *, local_ip: str | None = None
    ) -> bool:
        """Connect, handshake, discover, subscribe, and enter receive loop.

        Returns when connection drops or stop() is called. Returns True
        if at least one cycle of measurements was received.
        """
        await self._run_managed(host, port, local_ip)
        return bool(self._latest_measurements)

    async def start(self, host: str, port: int, *, local_ip: str | None = None) -> None:
        """Start connection in background task."""
        self._task = asyncio.create_task(self._run_managed(host, port, local_ip))

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        await self._cleanup()

    async def _run_managed(self, host: str, port: int, local_ip: str | None) -> None:
        self._running = True
        try:
            _LOGGER.info("Connecting to %s:%s", host, port)
            await self._run(host, port, local_ip)
        except asyncio.CancelledError:
            pass
        except Exception:
            _LOGGER.exception("Connection error")
        finally:
            self._running = False
            await self._cleanup()

    async def _run(self, host: str, port: int, local_ip: str | None) -> None:
        if local_ip is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                local_ip = "0.0.0.0"

        self._aiozc = AsyncZeroconf(ip_version=IPVersion.V4Only)
        handler = MDNSHandler(self._cert_ski)

        desc = {"txtvers": "1", "path": "/ship/", "ski": self._cert_ski, "register": "true"}
        info = AsyncServiceInfo(
            const.SHIP_SERVICE_TYPE,
            f"HomeAssistant-Vaillant-EEBUS.{const.SHIP_SERVICE_TYPE}",
            addresses=[socket.inet_aton(local_ip)],
            port=54885,
            properties=desc,
        )
        await self._aiozc.async_register_service(info)
        AsyncServiceBrowser(self._aiozc.zeroconf, const.SHIP_SERVICE_TYPE, handler)

        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_ctx.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        ssl_ctx.set_ciphers(const.TLS_CIPHERS)

        try:
            import websockets

            async with websockets.connect(
                f"wss://{host}:{port}/ship/",
                ssl=ssl_ctx,
                subprotocols=cast(Any, ["ship"]),
                open_timeout=const.WS_OPEN_TIMEOUT,
            ) as ws:
                self._ws = ws
                await ws.send(b"\x00\x00")

                success = await perform_ship_handshake(ws, self._local_ship_id)
                if not success:
                    _LOGGER.error("Handshake failed")
                    return

                _LOGGER.info("SHIP handshake successful")
                await self._receive_loop(ws)
        except OSError as e:
            _LOGGER.error("Connection failed: %s", e)
        finally:
            self._ws = None

    async def _receive_loop(self, ws: Any) -> None:
        message_count = 0
        remote_device_address: str | None = None
        discovery_requested = False
        remote_feature_map: dict[str, dict[str, Any]] = {}
        peer_use_case_received = False
        measurement_subscription_sent = False
        measurement_read_sent = False
        selected_measurement_servers: list[dict[str, Any]] = []

        def _desc_key_from_address(addr: Any) -> tuple[tuple[int, ...], int] | None:
            if not isinstance(addr, dict):
                return None
            ent = addr.get("entity")
            feat = addr.get("feature")
            if not (isinstance(ent, list) and ent and all(isinstance(x, int) for x in ent)):
                return None
            if not isinstance(feat, int):
                return None
            return (tuple(int(x) for x in ent), int(feat))

        while True:
            try:
                data = await asyncio.wait_for(ws.recv(), timeout=const.WS_RECV_TIMEOUT)
            except TimeoutError:
                try:
                    await send_ship_json(ws, {"connectionHello": {"phase": "ready", "waiting": const.HELLO_WAITING_MS}})
                except Exception:
                    pass
                continue

            message_count += 1

            if not isinstance(data, bytes) or len(data) == 0:
                continue

            if data[0] == 1:
                continue

            if data[0] != 2:
                continue

            try:
                payload_text = data[1:].decode("utf-8", errors="ignore")
                payload_text = json_from_eebus_json(payload_text)
                msg = json.loads(payload_text)

                parsed = _parse_spine_datagram(msg)
                if parsed is None:
                    continue

                hdr, cmd = parsed
                cmd_classifier = hdr.get("cmdClassifier")
                ack_req = hdr.get("ackRequest")

                if self._spine_message_callback:
                    try:
                        self._spine_message_callback(hdr, cmd, cmd_classifier)
                    except Exception:
                        pass

                if remote_device_address is None:
                    addr_src = hdr.get("addressSource")
                    if isinstance(addr_src, dict):
                        dev = addr_src.get("device")
                        if isinstance(dev, str) and dev:
                            remote_device_address = dev

                if remote_device_address is not None and not discovery_requested:
                    discovery_requested = True
                    await request_remote_detailed_discovery(
                        ws,
                        local_device_address=self._local_device_address,
                        remote_device_address=remote_device_address,
                        msg_counter=self._msg_counter,
                    )

                try:
                    if cmd_classifier != "result":
                        await send_spine_result_ok(
                            ws,
                            request_header=hdr,
                            local_device_address=self._local_device_address,
                            msg_counter=self._msg_counter,
                        )

                    if cmd_classifier == "read":
                        await handle_spine_read(
                            ws,
                            request_header=hdr,
                            cmd=cmd,
                            local_device_address=self._local_device_address,
                            msg_counter=self._msg_counter,
                        )

                    elif cmd_classifier == "reply":
                        if "nodeManagementDetailedDiscoveryData" in cmd:
                            discovery = cmd.get("nodeManagementDetailedDiscoveryData")
                            if isinstance(discovery, dict):
                                hp_entity, feature_map = _extract_remote_landmap(discovery)
                                remote_feature_map.update(feature_map)
                                self._remote_entities = _extract_entities(discovery)
                                self._remote_measurement_servers = _extract_measurement_servers(discovery)

                                self._device_info = {
                                    "entities": self._remote_entities,
                                    "feature_map": remote_feature_map,
                                    "remote_device_address": remote_device_address,
                                }

                                if self._remote_measurement_servers:
                                    selected_measurement_servers = list(self._remote_measurement_servers)

                                if remote_device_address is not None:
                                    await request_remote_node_management_use_case_data(
                                        ws,
                                        local_device_address=self._local_device_address,
                                        remote_device_address=remote_device_address,
                                        msg_counter=self._msg_counter,
                                    )

                        elif "nodeManagementUseCaseData" in cmd:
                            peer_use_case_received = True
                            if not selected_measurement_servers and self._remote_measurement_servers:
                                selected_measurement_servers = list(self._remote_measurement_servers)

                        elif "measurementDescriptionListData" in cmd:
                            desc_map = parse_measurement_description(cmd)
                            key = _desc_key_from_address(hdr.get("addressSource"))
                            if key is not None and desc_map:
                                self._measurement_desc_maps[key] = desc_map

                        elif "measurementListData" in cmd:
                            key = _desc_key_from_address(hdr.get("addressSource"))
                            desc_map = self._measurement_desc_maps.get(key, {}) if key is not None else {}
                            updates = parse_measurement_list(
                                cmd,
                                desc_map,
                                source_address=hdr.get("addressSource") if isinstance(hdr, dict) else None,
                            )
                            self._process_measurement_updates(updates)

                    elif cmd_classifier == "notify":
                        if "measurementDescriptionListData" in cmd:
                            desc_map = parse_measurement_description(cmd)
                            key = _desc_key_from_address(hdr.get("addressSource"))
                            if key is not None and desc_map:
                                self._measurement_desc_maps[key] = desc_map

                        elif "measurementListData" in cmd:
                            key = _desc_key_from_address(hdr.get("addressSource"))
                            desc_map = self._measurement_desc_maps.get(key, {}) if key is not None else {}
                            updates = parse_measurement_list(
                                cmd,
                                desc_map,
                                source_address=hdr.get("addressSource") if isinstance(hdr, dict) else None,
                            )
                            self._process_measurement_updates(updates)

                    if (
                        peer_use_case_received
                        and remote_device_address is not None
                        and selected_measurement_servers
                        and not measurement_subscription_sent
                    ):
                        measurement_subscription_sent = True
                        for server in selected_measurement_servers:
                            await subscribe_remote_measurement(
                                ws,
                                local_device_address=self._local_device_address,
                                remote_device_address=remote_device_address,
                                remote_measurement_feature=server,
                                msg_counter=self._msg_counter,
                            )

                    if (
                        peer_use_case_received
                        and remote_device_address is not None
                        and selected_measurement_servers
                        and not measurement_read_sent
                    ):
                        measurement_read_sent = True
                        for server in selected_measurement_servers:
                            await request_remote_measurement_once(
                                ws,
                                local_device_address=self._local_device_address,
                                remote_device_address=remote_device_address,
                                remote_measurement_feature=server,
                                msg_counter=self._msg_counter,
                            )

                except Exception:
                    _LOGGER.exception("SPINE processing error")

            except Exception:
                _LOGGER.exception("Message decode error")

    def _process_measurement_updates(self, updates: list[dict[str, Any]]) -> None:
        for u in updates:
            scope = str(u.get("scopeType") or "unknown")
            unit = _unit_to_ha(u.get("unit"))
            mid = u.get("measurementId")
            src = u.get("source") if isinstance(u.get("source"), dict) else {}
            ent = src.get("entity") if isinstance(src, dict) else None
            feat = src.get("feature") if isinstance(src, dict) else None

            object_id = _slug(
                f"{scope}_e{'_'.join(str(x) for x in ent) if isinstance(ent, list) else 'na'}_f{feat if isinstance(feat, int) else 'na'}_id{mid}"
            )

            self._latest_measurements[object_id] = {
                "value": u.get("value"),
                "unit": unit,
                "scopeType": scope,
                "measurementId": mid,
                "source": src,
                "ts": time.time(),
            }

            if self._publish_jsonl:
                print(json.dumps(
                    {"type": "measurement", "object_id": object_id, **self._latest_measurements[object_id]},
                    ensure_ascii=False, separators=(",", ":"),
                ))

        if updates and self._measurement_callback:
            try:
                if asyncio.iscoroutinefunction(self._measurement_callback):
                    asyncio.ensure_future(self._measurement_callback(self._latest_measurements))
                else:
                    self._measurement_callback(self._latest_measurements)
            except Exception:
                _LOGGER.exception("Measurement callback error")

    async def _cleanup(self) -> None:
        if self._aiozc:
            try:
                await self._aiozc.async_unregister_all_services()
                await self._aiozc.async_close()
            except Exception:
                pass
            self._aiozc = None
        self._ws = None
