"""fortigate_Stats integration."""
from .const import *
import voluptuous as vol
import asyncio

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_PORT
)

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    """Set up a skeleton component."""
    return True

async def async_setup_entry(hass, config_entry):

    hass.async_add_job(hass.config_entries.async_forward_entry_setup(config_entry, "sensor"))
    config_entry.add_update_listener(update_listener)

    return True
    
    def _stop_monitor(_event):
        monitor.stopped=True
        #hass.states.async_set
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, _stop_monitor)
        LOGGER.error('Init done')
        return True

### TESTING ###
async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""
    await asyncio.gather(
        *[
            hass.config_entries.async_forward_entry_unload(config_entry, platform)
            for platform in PLATFORMS
        ]
    )
    LOGGER.error("Successfully removed the FortiGate Stats integration")

    return True
### TESTING ###

async def update_listener(hass, entry):
    hass.data[DOMAIN][entry.entry_id]["monitor"].updateIntervalSeconds=entry.options.get(CONF_SCAN_INTERVAL)
