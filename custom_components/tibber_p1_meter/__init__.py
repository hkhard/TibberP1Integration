"""The Tibber P1 Meter integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from tibber import Tibber
from tibber.exceptions import TibberAPIException

from .const import DOMAIN, SCAN_INTERVAL

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Tibber P1 Meter component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tibber P1 Meter from a config entry."""
    _LOGGER.debug("Setting up Tibber P1 Meter integration")

    access_token = entry.data.get(CONF_ACCESS_TOKEN)
    if not access_token:
        _LOGGER.error("No Tibber API access token provided")
        return False

    try:
        _LOGGER.debug("Attempting to connect to Tibber API")
        tibber_connection = Tibber(access_token, timeout=30)
        await tibber_connection.update_info()
        
        if not tibber_connection.valid_access_token:
            _LOGGER.error("Invalid Tibber API access token")
            raise ConfigEntryNotReady("Invalid Tibber API access token")

        _LOGGER.debug("Successfully connected to Tibber API")

        homes = tibber_connection.get_homes()
        if not homes:
            _LOGGER.error("No Tibber homes found")
            raise ConfigEntryNotReady("No Tibber homes found")

        home = homes[0]  # Assuming the first home
        home_id = home.home_id

        _LOGGER.debug(f"Found Tibber home with ID: {home_id}")

    except TibberAPIException as err:
        _LOGGER.error("Failed to connect to Tibber API: %s", err)
        raise ConfigEntryNotReady(f"Failed to connect to Tibber API: {err}") from err
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while connecting to Tibber API")
        raise ConfigEntryNotReady("Timeout while connecting to Tibber API")
    except Exception as err:
        _LOGGER.error("Unexpected error while setting up Tibber P1 Meter: %s", err)
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    coordinator = TibberP1MeterCoordinator(hass, tibber_connection, home_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class TibberP1MeterCoordinator(DataUpdateCoordinator):
    """Class to manage fetching P1 meter data."""

    def __init__(self, hass: HomeAssistant, tibber_connection, home_id: str):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.tibber_connection = tibber_connection
        self.home_id = home_id

    async def _async_update_data(self):
        """Fetch data from P1 meter and update Tibber."""
        try:
            _LOGGER.debug("Fetching P1 meter data")
            p1_data = await self._fetch_p1_meter_data()
            
            _LOGGER.debug("Sending data to Tibber API")
            await self.tibber_connection.send_rt_update(self.home_id, p1_data)
            _LOGGER.debug("Successfully sent data to Tibber API")
            return p1_data
        except TibberAPIException as err:
            _LOGGER.error("Error communicating with Tibber API: %s", err)
            raise UpdateFailed(f"Error communicating with Tibber API: {err}")
        except Exception as err:
            _LOGGER.error("Unexpected error while updating data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}")

    async def _fetch_p1_meter_data(self):
        """Fetch data from P1 meter using Home Assistant energy sensors."""
        try:
            _LOGGER.debug("Fetching P1 meter data from Home Assistant sensors")
            energy_consumption = await self.hass.states.async_get("sensor.energy_consumption_kwh")
            current_power = await self.hass.states.async_get("sensor.current_power_w")
            energy_production = await self.hass.states.async_get("sensor.energy_production_kwh")
            current_power_production = await self.hass.states.async_get("sensor.current_power_production_w")

            data = {
                "power": float(current_power.state) if current_power else 0,
                "powerProduction": float(current_power_production.state) if current_power_production else 0,
                "accumulatedConsumption": float(energy_consumption.state) if energy_consumption else 0,
                "accumulatedProduction": float(energy_production.state) if energy_production else 0,
                "accumulatedCost": 0,  # This information is not available from energy sensors
                "currency": "EUR"
            }
            _LOGGER.debug("Fetched P1 meter data: %s", data)
            return data
        except Exception as err:
            _LOGGER.error("Error fetching P1 meter data from Home Assistant: %s", err)
            raise
