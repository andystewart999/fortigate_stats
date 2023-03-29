"""Adds config flow for ESXi Stats."""
import logging
from collections import OrderedDict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

# from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    DEFAULT_PORT,
)
from .snmp import snmp_get
from .snmp import snmp_getmulti


_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class ESXIiStatslowHandler(config_entries.ConfigFlow):
    """Config flow for ESXi Stats."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SNMPStatsOptionsFlow(config_entry)

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input={}):
        """Handle a flow initialized by the user."""
        self._errors = {}
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Check if entered host is already in HomeAssistant
            existing = await self._check_existing(user_input["host"])
            if existing:
                return self.async_abort(reason="already_configured")

            # If it is not, continue with communication test
            valid, hostname = await self.hass.async_add_executor_job(
                self._test_communication,
                user_input["host"],
                user_input["port"],
                user_input["username"],
            )
            if valid:
                # Need to turn hostname into something Home Assistant is OK with
                return self.async_create_entry(
                    title=hostname, data=user_input
                )
            else:
                self._errors["base"] = "communication"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""
        # Defaults
        host = ""
        port = DEFAULT_PORT
        username = ""

        if user_input is not None:
            if "hostname" in user_input:
                host = user_input["hostname"]
            if "port" in user_input:
                port = user_input["port"]
            if "username" in user_input:
                username = user_input["username"]
 #           if "datastore" in user_input:
 #               datastore = user_input["datastore"]
 
        data_schema = OrderedDict()
        data_schema[vol.Required("host", default="10.0.0.1")] = str
        data_schema[vol.Required("username", default="admin")] = str
        data_schema[vol.Required("port", default=port)] = int
        data_schema[vol.Required("monitor_cpu_ram", default=True)] = bool
        data_schema[vol.Required("monitor_disk_usage", default=True)] = bool
        data_schema[vol.Required("monitor_session_count", default=True)] = bool
        data_schema[vol.Required("monitor_sdwan_interfaces", default=True)] = bool
       
        return self.async_show_form(
            step_id="user1", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _check_existing(self, host):
        for entry in self._async_current_entries():
            if host == entry.data.get("host"):
                return True

    def _test_communication(self, host, port, username):
        """Return true if the communication is ok."""
        try:
            conn = False
            hostname = ''
            oid = '1.3.6.1.2.1.1.5.0'
            hostname = snmp_get(host, username, port, oid)
            _LOGGER.error (hostname)
#            oids = (oid,)
#            _LOGGER.error ("calling snmp_getmulti")
#            varBinds = snmp_getmulti(host, username, port, oids)
#            for oid, val in varBinds:
#                hostname = val
#            hostname = varBinds[0][1]
#            _LOGGER.error(hostname)
            if (hostname != ""):
                conn = True
            _LOGGER.error(conn)

            return conn, "fortigate100d"
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(exception)
            return False


class SNMPStatsOptionsFlow(config_entries.OptionsFlow):
    """Handle FortiGate Stats options"""

    def __init__(self, config_entry):
        """Initialize FortiGate Stats options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

#    async def async_step_init(self, user_input=None):
#        """Manage FortiGate Stats options."""
#        return await self.async_step_esxi_options()
#
#    async def async_step_esxi_options(self, user_input=None):
#        """Manage FortiGate Stats Options."""
#        if user_input is not None:
#            self.options[CONF_HOST_STATE] = user_input[CONF_HOST_STATE]
#            self.options[CONF_DS_STATE] = user_input[CONF_DS_STATE]
#            self.options[CONF_LIC_STATE] = user_input[CONF_LIC_STATE]
#            self.options[CONF_VM_STATE] = user_input[CONF_VM_STATE]
#            return self.async_create_entry(title="", data=self.options)
#
#        return self.async_show_form(
#            step_id="snmp_options",
#            data_schema=vol.Schema(
#                {
#                    vol.Optional(
#                        CONF_HOST_STATE,
#                        default=self.config_entry.options.get(
#                            CONF_HOST_STATE, DEFAULT_HOST_STATE
#                        ),
#                    ): vol.In(VMHOST_STATES),
#                    vol.Optional(
#                        CONF_DS_STATE,
#                        default=self.config_entry.options.get(
#                            CONF_DS_STATE, DEFAULT_DS_STATE
#                        ),
#                    ): vol.In(DATASTORE_STATES),
#                    vol.Optional(
#                        CONF_LIC_STATE,
#                        default=self.config_entry.options.get(
#                            CONF_LIC_STATE, DEFAULT_LIC_STATE
#                        ),
#                    ): vol.In(LICENSE_STATES),
#                    vol.Optional(
#                        CONF_VM_STATE,
#                        default=self.config_entry.options.get(
#                            CONF_VM_STATE, DEFAULT_VM_STATE
#                        ),
#                    ): vol.In(VM_STATES),
#                }
#            ),
#        )
#
