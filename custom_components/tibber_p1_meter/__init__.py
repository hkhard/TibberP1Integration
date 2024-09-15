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
from tibber import Tibber

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(minutes=5)

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

    hass.data[DOMAIN][entry.entry_id] = tibber_connection

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def update_tibber_data(now):
        """Fetch data from P1 meter and update Tibber."""
        # TODO: Implement fetching data from P1 meter
        # For now, we'll use dummy data
        dummy_data = {
            "power": 1000,
            "powerProduction": 0,
            "accumulatedConsumption": 5000,
            "accumulatedProduction": 0,
            "accumulatedCost": 10,
            "currency": "EUR"
        }

        try:
            await tibber_connection.send_rt_update(dummy_data)
            _LOGGER.info("Successfully sent data to Tibber API")
        except Exception as err:
            _LOGGER.error("Failed to send data to Tibber API: %s", err)

    # Schedule periodic updates
    hass.helpers.event.async_track_time_interval(
        update_tibber_data, SCAN_INTERVAL
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
