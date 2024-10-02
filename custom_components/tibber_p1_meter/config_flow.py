"""Config flow for Tibber P1 Meter integration."""
from __future__ import annotations

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig
from homeassistant.helpers.entity_registry import async_get
import aiohttp

from .const import DOMAIN, CONF_ENERGY_CONSUMPTION, CONF_CURRENT_POWER, CONF_ENERGY_PRODUCTION, CONF_CURRENT_POWER_PRODUCTION, CONF_P1_METER_ENTITY

_LOGGER = logging.getLogger(__name__)

class TibberP1MeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber P1 Meter."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.data = {}

    def _reset_flow(self):
        """Reset the flow."""
        self.data = {}
        _LOGGER.debug("Returning from async_step_user")
        return self.async_step_user()

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting Tibber P1 Meter config flow")
        _LOGGER.debug(f"async_step_select_p1_meter called. self.data: {self.data}")
        errors = {}

        if user_input is not None:
            try:
                _LOGGER.debug("Validating Tibber API access token")
                await self._validate_input(user_input[CONF_ACCESS_TOKEN])
                self.data[CONF_ACCESS_TOKEN] = user_input[CONF_ACCESS_TOKEN]
                _LOGGER.debug(f"Stored access token: {self.data[CONF_ACCESS_TOKEN]}")
                _LOGGER.debug("Tibber API access token validated successfully")
                return await self.async_step_select_p1_meter()
            except aiohttp.ClientError as err:
                _LOGGER.error("Failed to connect to Tibber API: %s", err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                _LOGGER.error("Invalid Tibber API access token: %s", err)
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error during Tibber API validation: %s", err)
                return self._reset_flow()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): str}),
            errors=errors,
        )

    async def async_step_select_p1_meter(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the P1 meter selection step."""
        if CONF_ACCESS_TOKEN not in self.data:
            _LOGGER.warning("Access token missing, resetting flow")
            return self._reset_flow()

        _LOGGER.debug("Starting P1 meter selection step")
        errors = {}

        if user_input is not None:
            self.data[CONF_P1_METER_ENTITY] = user_input[CONF_P1_METER_ENTITY]
            _LOGGER.debug("Selected P1 meter entity: %s", self.data[CONF_P1_METER_ENTITY])
            return await self.async_step_select_entities()

        # Get all sensor entities
        entity_registry = await async_get(self.hass)
        sensor_entities = [
            entity_id for entity_id, entry in entity_registry.entities.items()
            if entry.domain == "sensor"
        ]
        _LOGGER.debug("Found %d sensor entities", len(sensor_entities))
        _LOGGER.debug(f"Found sensor entities: {sensor_entities}")

        return self.async_show_form(
            step_id="select_p1_meter",
            data_schema=vol.Schema({
                vol.Required(CONF_P1_METER_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="sensor", multiple=False)
                )
            })
            _LOGGER.debug("Showing P1 meter selection form"),
            errors=errors,
        )

    async def async_step_select_entities(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """Handle the entity selection step."""
        if CONF_ACCESS_TOKEN not in self.data or CONF_P1_METER_ENTITY not in self.data:
            _LOGGER.warning("Missing required data, resetting flow")
            return self._reset_flow()

        _LOGGER.debug("Starting entity selection step")
        errors = {}

        if user_input is not None:
            self.data.update(user_input)
            _LOGGER.debug("Selected entities: %s", user_input)
            if all(key in self.data for key in [CONF_ACCESS_TOKEN, CONF_P1_METER_ENTITY, CONF_ENERGY_CONSUMPTION, CONF_CURRENT_POWER]):
                return self.async_create_entry(title="Tibber P1 Meter", data=self.data)
            else:
                _LOGGER.warning("Missing required configuration data, resetting flow")
                return self._reset_flow()

        # Get the available entities from the selected P1 meter
        p1_meter_entity = self.data[CONF_P1_METER_ENTITY]
        available_entities = await self._get_available_entities(p1_meter_entity)
        _LOGGER.debug("Found %d available entities for P1 meter %s", len(available_entities), p1_meter_entity)

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
        _LOGGER.debug("Validating Tibber API access token")
        session = async_get_clientsession(self.hass)
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.get("https://api.tibber.com/v1-beta/gql", headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Invalid Tibber API authentication. Status code: %d", resp.status)
                raise ValueError(f"Invalid authentication. Status code: {resp.status}")
        _LOGGER.debug("Tibber API access token validated successfully")

    async def _get_available_entities(self, p1_meter_entity: str) -> list[str]:
        """Get available entities from the selected P1 meter."""
        _LOGGER.debug("Getting available entities for P1 meter: %s", p1_meter_entity)
        entity_registry = await async_get(self.hass)
        device_id = entity_registry.async_get(p1_meter_entity).device_id

        if device_id is None:
            _LOGGER.warning("No device ID found for P1 meter entity: %s", p1_meter_entity)
            return []

        available_entities = [
            entity_id for entity_id, entry in entity_registry.entities.items()
            if entry.device_id == device_id
        ]
        _LOGGER.debug("Found %d available entities for P1 meter %s", len(available_entities), p1_meter_entity)
        return available_entities
