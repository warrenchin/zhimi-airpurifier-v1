"""Switches for the Mochi Zhimi Purifier V1.

The Power switch is mode-based: this firmware has no working power
property or set_power method (verified: method_not_supported). Its
standby is mode 'idle' with the motors at 0, and setting any run
mode wakes it — the same thing the Xiaomi Home app achieves through
the cloud. The switch state is therefore always truthful: it is on
exactly when the device's mode is not 'idle'.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ZhimiV1Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            PowerSwitch(coordinator, entry),
            LedSwitch(coordinator, entry),
            BuzzerSwitch(coordinator, entry),
        ]
    )


class PowerSwitch(ZhimiV1Entity, SwitchEntity):
    _attr_name = "Power"
    _attr_icon = "mdi:power"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "power")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("mode") != "idle"

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_mode(self.coordinator.last_run_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_mode("idle")


class _OnOffSwitch(ZhimiV1Entity, SwitchEntity):
    """Base for the simple on/off string properties."""

    _prop: str = ""

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get(self._prop) == "on"


class LedSwitch(_OnOffSwitch):
    _attr_name = "LED"
    _attr_icon = "mdi:led-on"
    _prop = "led"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "led")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_led(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_led(False)


class BuzzerSwitch(_OnOffSwitch):
    _attr_name = "Buzzer"
    _attr_icon = "mdi:volume-high"
    _prop = "buzzer"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "buzzer")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_buzzer(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_buzzer(False)
