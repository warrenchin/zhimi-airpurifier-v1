"""DataUpdateCoordinator for the Mochi Zhimi Purifier V1."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from miio import DeviceException

from .client import ZhimiV1Client
from .const import DEFAULT_RUN_MODE, DOMAIN, SCAN_SECONDS

_LOGGER = logging.getLogger(__name__)


class ZhimiV1Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the purifier's working properties and brokers writes."""

    def __init__(
        self, hass: HomeAssistant, client: ZhimiV1Client, name: str
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name}",
            update_interval=timedelta(seconds=SCAN_SECONDS),
        )
        self.client = client
        # Last non-idle mode, restored when the power switch turns on.
        self.last_run_mode: str = DEFAULT_RUN_MODE

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.hass.async_add_executor_job(self.client.fetch)
        except DeviceException as err:
            raise UpdateFailed(f"Error communicating with purifier: {err}") from err
        if data.get("mode") and data["mode"] != "idle":
            self.last_run_mode = data["mode"]
        return data

    def _patch(self, **changes: Any) -> None:
        """Apply a local state patch after a successful write."""
        if self.data is None:
            return
        new_data = {**self.data, **changes}
        if new_data.get("mode") and new_data["mode"] != "idle":
            self.last_run_mode = new_data["mode"]
        self.async_set_updated_data(new_data)

    async def async_set_mode(self, mode: str) -> None:
        await self.hass.async_add_executor_job(self.client.set_mode, mode)
        self._patch(mode=mode)

    async def async_set_led(self, on: bool) -> None:
        await self.hass.async_add_executor_job(self.client.set_led, on)
        self._patch(led="on" if on else "off")

    async def async_set_buzzer(self, on: bool) -> None:
        await self.hass.async_add_executor_job(self.client.set_buzzer, on)
        self._patch(buzzer="on" if on else "off")

    async def async_reset_filter(self) -> None:
        await self.hass.async_add_executor_job(self.client.reset_filter)
        await self.async_request_refresh()
