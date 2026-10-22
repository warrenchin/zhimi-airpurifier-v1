"""Buttons for the Mochi Zhimi Purifier V1."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    async_add_entities([ResetFilterButton(coordinator, entry)])


class ResetFilterButton(ZhimiV1Entity, ButtonEntity):
    _attr_name = "Reset Filter"
    _attr_icon = "mdi:air-filter-outline"

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, "reset_filter")

    async def async_press(self) -> None:
        await self.coordinator.async_reset_filter()
