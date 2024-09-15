
"""The Tibber P1 Meter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from tibber import Tibber
from tibber.exceptions import TibberConnectionError, TibberResponseError

from .const import DOMAIN

PLATFORMS: list[str] = ["sensor"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tibber P1 Meter from a config entry."""
    tibber = Tibber(access_token=entry.data[CONF_ACCESS_TOKEN])

    try:
        await hass.async_add_executor_job(tibber.update_info)
    except (TibberConnectionError, TibberResponseError) as err:
        raise ConfigEntryNotReady(f"Failed to connect to Tibber API: {err}") from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "tibber_connection": tibber,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

        # Close the Tibber connection
        tibber_connection: Tibber = hass.data[DOMAIN][entry.entry_id]["tibber_connection"]
        await hass.async_add_executor_job(tibber_connection.close_connection)

    return unload_ok
