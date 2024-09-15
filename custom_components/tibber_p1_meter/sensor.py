"""Sensor platform for Tibber P1 Meter integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    CURRENCY_EURO,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import TibberP1MeterCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the Tibber P1 Meter sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        TibberP1PowerSensor(coordinator),
        TibberP1EnergyConsumptionSensor(coordinator),
        TibberP1EnergyCostSensor(coordinator),
    ])

class TibberP1Sensor(CoordinatorEntity, SensorEntity):
    """Base class for Tibber P1 Meter sensors."""

    def __init__(self, coordinator: TibberP1MeterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{self.entity_description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "Tibber P1 Meter",
            "manufacturer": "Custom",
            "model": "P1 Meter",
        }

class TibberP1PowerSensor(TibberP1Sensor):
    """Sensor for current power consumption."""

    _attr_name = "Tibber P1 Power"
    _attr_native_unit_of_measurement = POWER_WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        """Return the current power consumption."""
        return self.coordinator.data.get("power")

class TibberP1EnergyConsumptionSensor(TibberP1Sensor):
    """Sensor for accumulated energy consumption."""

    _attr_name = "Tibber P1 Energy Consumption"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the accumulated energy consumption."""
        return self.coordinator.data.get("accumulatedConsumption")

class TibberP1EnergyCostSensor(TibberP1Sensor):
    """Sensor for accumulated energy cost."""

    _attr_name = "Tibber P1 Energy Cost"
    _attr_native_unit_of_measurement = CURRENCY_EURO
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> StateType:
        """Return the accumulated energy cost."""
        return self.coordinator.data.get("accumulatedCost")
