import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_PORT
)
LOGGER = logging.getLogger(__package__)

DOMAIN = "fortigate_stats"
DEFAULT_SCAN_INTERVAL = 10

#OIDS
OID_HOSTNAME = '1.3.6.1.2.1.1.5.0'
OID_SERIALNUMBER = '1.3.6.1.4.1.12356.100.1.1.1.0'
OID_MODEL = '1.3.6.1.2.1.1.1'
OID_CPUUSAGE = '1.3.6.1.4.1.12356.101.4.1.3.0'
OID_RAMUSAGE = '1.3.6.1.4.1.12356.101.4.1.4.0'
OID_FORTIOS = '1.3.6.1.4.1.12356.101.4.1.1.0'

CONFIG_SCHEMA_A=vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_PORT, default=161): int,
                vol.Required("cpu_and_ram"): bool,
                vol.Required("disk"): bool,
                vol.Required("sessions"): bool,
                vol.Optional(CONF_SCAN_INTERVAL, default=10): int
            }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: CONFIG_SCHEMA_A
    },
    extra=vol.ALLOW_EXTRA,
)


#def flattenObj(prefix,seperator,obj):
#    result={}
#    for field in obj:
#        val=obj[field]
#        valprefix=prefix+seperator+field
#        if type(val) is dict:
#            sub=flattenObj(valprefix,seperator,val)
#            result.update(sub)
#        else:
#            result[valprefix]=val
#    return result