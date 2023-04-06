from .snmp import snmp_getmulti
import traceback
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
# pylint: disable=unused-wildcard-import
from .const import * # 
# pylint: enable=unused-wildcard-import
import voluptuous as vol
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_PORT
)


class ConfigFlowHandler(config_entries.ConfigFlow,domain=DOMAIN):
    def __init__(self):
        """Initialize."""
        self.data_schema = CONFIG_SCHEMA_A
    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        #if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return self._show_form()

        username = user_input[CONF_USERNAME]
        ipaddress = user_input[CONF_IP_ADDRESS]
        port = user_input[CONF_PORT]
                        
        try:
            #We only need to get this information once, so get it as part of the connection test and add it to user_input
            oids = (OID_HOSTNAME, OID_SERIALNUMBER, OID_MODEL,OID_FORTIOS)
            errorIndication, oidReturn = snmp_getmulti(ipaddress, username, port, oids)
            
            if not errorIndication:
                user_input[OID_HOSTNAME] = oidReturn[0][1].prettyPrint()
                user_input[OID_SERIALNUMBER] = oidReturn[1][1].prettyPrint()
                user_input[OID_MODEL] = oidReturn[2][1].prettyPrint()
                user_input[OID_FORTIOS] = oidReturn[3][1].prettyPrint()
            
        except:
            e = traceback.format_exc()
            LOGGER.error("Unable to connect to snmp: %s", e)
            #if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form({"base": "connection_error"})
        
        return self.async_create_entry(
            title=user_input[OID_HOSTNAME],
            data=user_input
        )

    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""

        return await self.async_step_user(import_config)
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)


    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): cv.positive_int,
                }
            )

        )
    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title="", data=self.options)