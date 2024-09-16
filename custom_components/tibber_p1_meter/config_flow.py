"""Config flow for Tibber P1 Meter integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig
import aiohttp

from .const import DOMAIN, CONF_ENERGY_CONSUMPTION, CONF_CURRENT_POWER, CONF_ENERGY_PRODUCTION, CONF_CURRENT_POWER_PRODUCTION

class TibberP1MeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber P1 Meter."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.data = {}

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                await self._validate_input(user_input[CONF_ACCESS_TOKEN])
                self.data[CONF_ACCESS_TOKEN] = user_input[CONF_ACCESS_TOKEN]
                return await self.async_step_select_entities()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): str}),
            errors=errors,
        )

    async def async_step_select_entities(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the entity selection step."""
        errors = {}

        if user_input is not None:
            self.data.update(user_input)
            return self.async_create_entry(title="Tibber P1 Meter", data=self.data)

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema({
                vol.Required(CONF_ENERGY_CONSUMPTION): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Required(CONF_CURRENT_POWER): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(CONF_ENERGY_PRODUCTION): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(CONF_CURRENT_POWER_PRODUCTION): EntitySelector(EntitySelectorConfig(domain="sensor")),
            }),
            errors=errors,
        )

    async def _validate_input(self, access_token: str) -> None:
        """Validate the user input allows us to connect."""
        session = async_get_clientsession(self.hass)
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get("https://api.tibber.com/v1-beta/gql", headers=headers) as resp:
            if resp.status != 200:
                raise ValueError("Invalid authentication")
