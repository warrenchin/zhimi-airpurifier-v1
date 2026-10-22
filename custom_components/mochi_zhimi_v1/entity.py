"""Shared entity base for the Mochi Zhimi Purifier V1."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODEL
from .coordinator import ZhimiV1Coordinator


class ZhimiV1Entity(CoordinatorEntity[ZhimiV1Coordinator]):
    """Base entity bound to the purifier's coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: ZhimiV1Coordinator, entry: ConfigEntry, key: str
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Zhimi",
            model=MODEL,
        )
