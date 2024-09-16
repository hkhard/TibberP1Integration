"""Constants for the Tibber P1 Meter integration."""
from datetime import timedelta

DOMAIN = "tibber_p1_meter"
SCAN_INTERVAL = timedelta(minutes=5)

CONF_P1_METER_ENTITY = "p1_meter_entity"
CONF_ENERGY_CONSUMPTION = "energy_consumption"
CONF_CURRENT_POWER = "current_power"
CONF_ENERGY_PRODUCTION = "energy_production"
CONF_CURRENT_POWER_PRODUCTION = "current_power_production"
