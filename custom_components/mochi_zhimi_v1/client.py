"""Thin miio client for the zhimi.airpurifier.v1, raw get_prop/send only.

Uses exactly the wire calls verified against Warren's unit on
2026-10-20 (via miiocli raw_command from artemis).
"""

from __future__ import annotations

import math
from typing import Any

from miio import Device, DeviceException

from .const import PROPS


class ZhimiV1Client:
    """Synchronous client; call through the executor."""

    def __init__(self, host: str, token: str) -> None:
        self._device = Device(host, token)
        self.host = host

    def info(self) -> dict[str, Any]:
        """Return device info (model, mac, firmware)."""
        info = self._device.info()
        return {
            "model": info.model,
            "mac": info.mac_address,
            "firmware_version": info.firmware_version,
            "hardware_version": info.hardware_version,
        }

    def fetch(self) -> dict[str, Any]:
        """Read all working properties in a single get_prop call."""
        values = self._device.send("get_prop", PROPS)
        return dict(zip(PROPS, values))

    def set_mode(self, mode: str) -> None:
        self._device.send("set_mode", [mode])

    def set_led(self, on: bool) -> None:
        self._device.send("set_led", ["on" if on else "off"])

    def set_buzzer(self, on: bool) -> None:
        self._device.send("set_buzzer", ["on" if on else "off"])

    def reset_filter(self) -> None:
        # The method this firmware answers is "reset_filter1" (no
        # params) — exactly what python-miio's reset_filter() sends and
        # what reset the counter on 2026-10-20. "reset_filter_time" is
        # rejected (method_not_supported).
        self._device.send("reset_filter1")


def us_aqi_from_pm25(pm25: float | int | None) -> int | None:
    """Calculate the US EPA AQI for a PM2.5 concentration (ug/m3).

    Piecewise-linear over the EPA breakpoints; concentration truncated
    to 0.1 ug/m3 first, result rounded to the nearest integer, capped
    at 500. This is an instantaneous conversion of the current reading
    (not a 24 h NowCast average).
    """
    if pm25 is None:
        return None
    c = math.floor(float(pm25) * 10) / 10.0
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= c <= bp_hi:
            aqi = (i_hi - i_lo) / (bp_hi - bp_lo) * (c - bp_lo) + i_lo
            return int(aqi + 0.5)
    return 500 if c > 500.4 else 0


__all__ = ["ZhimiV1Client", "us_aqi_from_pm25", "DeviceException"]
