
"""Support for Tibber P1 Meter sensors."""
from __future__ import annotations

import logging
from asyncio import Lock

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from tibber import Tibber
from tibber.subscription_manager import DEFAULT_TIMEOUT

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tibber P1 Meter sensor."""
    tibber_connection = hass.data[DOMAIN][config_entry.entry_id]["tibber_connection"]
    async_add_entities([TibberP1MeterSensor(hass, config_entry, tibber_connection)])

class TibberP1MeterSensor(SensorEntity):
    """Representation of a Tibber P1 Meter sensor."""

    _attr_name = "Tibber P1 Meter Power Usage"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, tibber_connection: Tibber) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_power_usage"
        self.tibber_connection = tibber_connection
        self._update_lock = Lock()

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await mqtt.async_subscribe(
            self.hass, "p1meter/energy_usage", self._mqtt_message_received
        )

    @callback
    def _mqtt_message_received(self, message):
        """Handle received MQTT message."""
        try:
            value = float(message.payload)
            self.hass.async_create_task(self._async_update_state(value))
        except ValueError:
            _LOGGER.error("Invalid payload received: %s", message.payload)

    async def _async_update_state(self, value):
        """Update state and Tibber in a non-blocking way."""
        async with self._update_lock:
            self._attr_native_value = value
            self.async_write_ha_state()
            await self._update_tibber()

    async def _update_tibber(self) -> None:
        """Update Tibber with the latest power usage data."""
        if self._attr_native_value is not None:
            try:
                home = self.tibber_connection.get_homes()[0]  # Assuming single home
                await home.update_price_info()
                await home.send_power_consumption(self._attr_native_value, DEFAULT_TIMEOUT)
            except Exception as e:
                _LOGGER.error("Error updating Tibber: %s", str(e), exc_info=True)
