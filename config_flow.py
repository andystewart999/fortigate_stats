from .snmp import snmp_getmulti, snmp_getfromtable, snmp_getmultifromtable
import traceback
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
# pylint: disable=unused-wildcard-import
from .const import * # 
# pylint: enable=unused-wildcard-import
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
        #self.data_schema = CONFIG_SCHEMA_MAIN
        
    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        #if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            return self._show_form(
                step_id = "user",
                data_schema = vol.Schema(
                    {
                        vol.Required(CONF_USERNAME): str,
                        vol.Required(CONF_IP_ADDRESS): str,
                        vol.Optional(CONF_PORT, default = DEFAULT_PORT): int,
                        vol.Required(CONF_CPUANDRAM): bool,
                        vol.Required(CONF_DISK): bool,
                        vol.Required(CONF_SESSIONS): bool,
                        vol.Optional(CONF_SCAN_INTERVAL, default = DEFAULT_SCAN_INTERVAL): int,
                        vol.Optional(CONF_INTERFACESYESNO, default = True): bool,
                        vol.Optional(CONF_PERFORMANCESLASYESNO, default = False): bool
                    }
                ),
            )

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
            e = traceback.format_exec()
            LOGGER.error("Unable to connect to snmp: %s", e)
            #if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form({"base": "connection_error"})
        
        #Save the current data set
        self.user_input = user_input

        # Do we need to show the next flow forms?
        if user_input[CONF_INTERFACESYESNO]:
            return await self.async_step_interfaces()
        elif user_input[CONF_PERFORMANCESLASYESNO]:
            return await self.async_step_performanceslas()
        else:
            return self.async_create_entry(
                title=user_input[OID_HOSTNAME],
                data=user_input
            )

    async def async_step_interfaces(self,user_input2 = None):
        """Second page of the flow."""

        if not user_input2:
            #Prepare the form
            #Read all connected interface names and aliases

            username = self.user_input[CONF_USERNAME]
            ipaddress = self.user_input[CONF_IP_ADDRESS]
            port = self.user_input[CONF_PORT]
            
            oids = (OID_IFSTATUS, OID_IFNAME, OID_IFALIAS)

            errorIndication, snmp_data = snmp_getmultifromtable(ipaddress, username, port, oids)
            if not errorIndication:
                CONNECTED_INTERFACES = {}
                for status, name, alias in snmp_data:
                    if ( status[1] == 1):
                        #Include it in the list
                        #Get the right name
                        if ( alias[1].prettyPrint() != ""):
                            final_name = alias[1].prettyPrint()
                        else:
                            final_name = name[1].prettyPrint()

                        #Add it
                        CONNECTED_INTERFACES[name[0].prettyPrint()] = final_name
                            
            return self._show_form(
                step_id = "interfaces",
                data_schema = vol.Schema(
                    {
                        vol.Required(
                            CONF_INTERFACES): cv.multi_select(CONNECTED_INTERFACES),
                        vol.Optional(
                            CONF_INTERFACESBANDWIDTH, default = True): bool,
                        vol.Optional(
                            CONF_INTERFACESOCTETS, default = False): bool,
                    }
                ),
            )
                                
        user_input_combined = self.user_input | user_input2 
        self.user_input = user_input_combined

        # Do we need to show the next flow forms?
        if self.user_input[CONF_PERFORMANCESLASYESNO]:
            return await self.async_step_performanceslas()
        else:
            return self.async_create_entry(
                title=self.user_input[OID_HOSTNAME],
                data=self.user_input
            )
    
    async def async_step_performanceslas(self,user_input3 = None):
        """Second page of the flow."""

        if not user_input3:
            #Prepare the form
            #Read all performance SLA link names

            username = self.user_input[CONF_USERNAME]
            ipaddress = self.user_input[CONF_IP_ADDRESS]
            port = self.user_input[CONF_PORT]

            errorIndication, snmp_data = snmp_getfromtable(ipaddress, username, port, OID_PERFORMANCESLALINKNAME)
            if not errorIndication:
                PERFORMANCESLA_LINKS = {}
                for oid_entry in snmp_data:
                    for oid, oid_value in oid_entry:
                        PERFORMANCESLA_LINKS[oid.prettyPrint()] = oid_value.prettyPrint()
                            
            return self._show_form(
                step_id = "performanceslas",
                data_schema = vol.Schema(
                    {
                        vol.Required(
                            CONF_PERFORMANCESLAS): cv.multi_select(PERFORMANCESLA_LINKS),
                        vol.Optional(
                            CONF_PERFORMANCESLASSTATE, default = True): bool,
                        vol.Optional(
                            CONF_PERFORMANCESLASLINKMETRICS, default = True): bool,
                        vol.Optional(
                            CONF_PERFORMANCESLASBANDWIDTHPROBE, default = True): bool,
                    }
                ),
            )

        performanceslas = user_input3[CONF_PERFORMANCESLAS]
                        
        user_input_combined = self.user_input | user_input3
        self.user_input = user_input_combined
        return self.async_create_entry(
            title=self.user_input[OID_HOSTNAME],
            data=self.user_input
        )

    @callback
    def _show_form(self, step_id,data_schema,errors = None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id=step_id,
            data_schema=data_schema,
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
