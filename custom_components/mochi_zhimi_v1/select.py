"""Mode select for the Mochi Zhimi Purifier V1.

Options are the modes this firmware actually accepts via set_mode
(verified live): auto, silent, strong, idle. 'favorite' is rejected
by the unit (method_not_supported) and is not offered. Choosing
Idle puts the unit in standby; choosing a run mode wakes it.
"""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_LABELS
from .entity import ZhimiV1Entity

_LABEL_TO_WIRE = {label: wire for wire, label in MODE_LABELS.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([ModeSelect(coordinator, entry)])


class ModeSelect(ZhimiV1Entity, SelectEntity):
    _attr_name = "Mode"
    _attr_icon = "mdi:air-purifier"
    _attr_options = list(MODE_LABELS.values())

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "mode")

    @property
    def current_option(self) -> str | None:
        wire = self.coordinator.data.get("mode")
        return MODE_LABELS.get(wire)

    async def async_select_option(self, option: str) -> None:
        wire = _LABEL_TO_WIRE.get(option)
        if wire is not None:
            await self.coordinator.async_set_mode(wire)
