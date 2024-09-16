"""Config flow for Tibber P1 Meter integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig
from homeassistant.helpers.entity_registry import async_get
import aiohttp

from .const import DOMAIN, CONF_ENERGY_CONSUMPTION, CONF_CURRENT_POWER, CONF_ENERGY_PRODUCTION, CONF_CURRENT_POWER_PRODUCTION, CONF_P1_METER_ENTITY

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
                return await self.async_step_select_p1_meter()
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

    async def async_step_select_p1_meter(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the P1 meter selection step."""
        errors = {}

        if user_input is not None:
            self.data[CONF_P1_METER_ENTITY] = user_input[CONF_P1_METER_ENTITY]
            return await self.async_step_select_entities()

        # Get all sensor entities
        entity_registry = await async_get(self.hass)
        sensor_entities = [
            entity_id for entity_id, entry in entity_registry.entities.items()
            if entry.domain == "sensor"
        ]

        return self.async_show_form(
            step_id="select_p1_meter",
            data_schema=vol.Schema({
                vol.Required(CONF_P1_METER_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="sensor", multiple=False)
                )
            }),
            errors=errors,
        )

    async def async_step_select_entities(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the entity selection step."""
        errors = {}

        if user_input is not None:
            self.data.update(user_input)
            return self.async_create_entry(title="Tibber P1 Meter", data=self.data)

        # Get the available entities from the selected P1 meter
        p1_meter_entity = self.data[CONF_P1_METER_ENTITY]
        available_entities = await self._get_available_entities(p1_meter_entity)

        return self.async_show_form(
            step_id="select_entities",
            data_schema=vol.Schema({
                vol.Required(CONF_ENERGY_CONSUMPTION): EntitySelector(
                    EntitySelectorConfig(include_entities=available_entities, multiple=False)
                ),
                vol.Required(CONF_CURRENT_POWER): EntitySelector(
                    EntitySelectorConfig(include_entities=available_entities, multiple=False)
                ),
                vol.Optional(CONF_ENERGY_PRODUCTION): EntitySelector(
                    EntitySelectorConfig(include_entities=available_entities, multiple=False)
                ),
                vol.Optional(CONF_CURRENT_POWER_PRODUCTION): EntitySelector(
                    EntitySelectorConfig(include_entities=available_entities, multiple=False)
                ),
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

    async def _get_available_entities(self, p1_meter_entity: str) -> list[str]:
        """Get available entities from the selected P1 meter."""
        entity_registry = await async_get(self.hass)
        device_id = entity_registry.async_get(p1_meter_entity).device_id

        if device_id is None:
            return []

        return [
            entity_id for entity_id, entry in entity_registry.entities.items()
            if entry.device_id == device_id
        ]
