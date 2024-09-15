"""Config flow for Tibber P1 Meter integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from tibber import Tibber

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    tibber = Tibber(access_token=data[CONF_ACCESS_TOKEN])
    try:
        await tibber.update_info()
        homes = tibber.get_homes()
        if not homes:
            raise NoHomesError
    except Exception as error:
        _LOGGER.error("Error connecting to Tibber API: %s", error)
        raise CannotConnect from error

    return {"title": f"Tibber P1 Meter ({homes[0].address1})"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber P1 Meter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except NoHomesError:
                errors["base"] = "no_homes"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "tibber_url": "https://developer.tibber.com/settings/access-token"
            },
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class NoHomesError(HomeAssistantError):
    """Error to indicate no homes are available."""
