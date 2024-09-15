"""Config flow for Tibber P1 Meter integration."""
from homeassistant import config_entries

from .const import DOMAIN

class TibberP1MeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tibber P1 Meter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Implementation will be added later
        return self.async_show_form(step_id="user")
