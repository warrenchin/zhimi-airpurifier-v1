"""Config flow for the Mochi Zhimi Purifier V1."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .client import ZhimiV1Client
from .const import CONF_HOST, CONF_NAME, CONF_TOKEN, DOMAIN, MODEL

_LOGGER = logging.getLogger(__name__)

STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_NAME, default="Zhimi Purifier V1"): str,
    }
)


async def _validate(hass: HomeAssistant, host: str, token: str) -> dict[str, Any]:
    client = ZhimiV1Client(host, token)
    try:
        info = await hass.async_add_executor_job(client.info)
        await hass.async_add_executor_job(client.fetch)
    except Exception as err:
        raise InvalidDevice from err
    return info


class ZhimiV1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mochi Zhimi Purifier V1."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            token = user_input[CONF_TOKEN].strip()
            try:
                info = await _validate(self.hass, host, token)
            except InvalidDevice:
                errors["base"] = "cannot_connect"
            else:
                if info.get("model") and info["model"] != MODEL:
                    errors["base"] = "wrong_model"
                else:
                    await self.async_set_unique_id(info.get("mac") or host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data={CONF_HOST: host, CONF_TOKEN: token},
                    )
        return self.async_show_form(
            step_id="user", data_schema=STEP_SCHEMA, errors=errors
        )


class InvalidDevice(HomeAssistantError):
    """Raised when the device cannot be reached or read."""
