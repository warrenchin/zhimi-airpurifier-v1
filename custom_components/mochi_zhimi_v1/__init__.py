"""Mochi Zhimi Purifier V1 integration.

A deliberately small, local-only integration for the 1st-gen Mijia
Air Purifier (zhimi.airpurifier.v1). Only features verified working
on the hardware are exposed; see const.py for the honest list.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from miio import DeviceException

from .client import ZhimiV1Client
from .const import CONF_HOST, CONF_TOKEN, DOMAIN
from .coordinator import ZhimiV1Coordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = ZhimiV1Client(entry.data[CONF_HOST], entry.data[CONF_TOKEN])
    coordinator = ZhimiV1Coordinator(hass, client, entry.title)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # first poll failed; let HA retry
        raise ConfigEntryNotReady(str(err)) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
