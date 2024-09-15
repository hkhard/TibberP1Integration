"""The Tibber P1 Meter integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from tibber import Tibber

from .const import DOMAIN, SCAN_INTERVAL

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Tibber P1 Meter component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tibber P1 Meter from a config entry."""
    tibber_connection = Tibber(access_token=entry.data[CONF_ACCESS_TOKEN])
    
    try:
        await tibber_connection.update_info()
    except Exception as err:
        raise ConfigEntryNotReady from err

    coordinator = TibberP1MeterCoordinator(hass, tibber_connection)
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

    def __init__(self, hass: HomeAssistant, tibber_connection: Tibber):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.tibber_connection = tibber_connection

    async def _async_update_data(self):
        """Fetch data from P1 meter and update Tibber."""
        try:
            # TODO: Implement actual P1 meter data fetching
            # For now, we'll use dummy data
            p1_data = await self.hass.async_add_executor_job(self._fetch_p1_meter_data)
            
            await self.tibber_connection.send_rt_update(p1_data)
            return p1_data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with P1 meter or Tibber API: {err}")

    def _fetch_p1_meter_data(self):
        """Fetch data from P1 meter (dummy implementation)."""
        # TODO: Replace this with actual P1 meter data fetching
        return {
            "power": 1000,
            "powerProduction": 0,
            "accumulatedConsumption": 5000,
            "accumulatedProduction": 0,
            "accumulatedCost": 10,
            "currency": "EUR"
        }
