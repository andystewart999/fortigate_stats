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
CONF_CPUANDRAM = "cpu_and_ram"
CONF_DISK = "disk"
CONF_SESSIONS = "sessions"
CONF_INTERFACESYESNO = "interfacesyesno"
CONF_INTERFACES = "interfaces"
CONF_INTERFACESBANDWIDTH="interfacesbandwidth"
CONF_INTERFACESOCTETS="interfacesoctets"
CONF_PERFORMANCESLASYESNO = "performanceslasyesno"
CONF_PERFORMANCESLAS = "performanceslas"
CONF_PERFORMANCESLASLINKMETRICS = "performanceslaslinkmetrics"
CONF_PERFORMANCESLASBANDWIDTHPROBE = "performanceslasbandwidthprobe"
CONF_PERFORMANCESLASSTATE = "performanceslasstate"

PERFORMANCESLAS_STATE = {
                    "0": "Alive",
                    "1": "Dead"
                }

PERFORMANCESLAS_ICON = {
                    "0": "mdi:timeline-check-outline",
                    "1": "mdi:timeline-remove-outline"
                }
    

LOGGER = logging.getLogger(__package__)

DOMAIN = "fortigate_stats"
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_PORT = 161
PLATFORMS = ["sensor"]

#OIDS
OID_HOSTNAME = '1.3.6.1.2.1.1.5.0'
OID_SERIALNUMBER = '1.3.6.1.4.1.12356.100.1.1.1.0'
OID_FORTIOS = '1.3.6.1.4.1.12356.101.4.1.1.0'
OID_MODEL = '1.3.6.1.4.1.12356.101.13.2.1.1.2.1'

OID_CPUUSAGE = '1.3.6.1.4.1.12356.101.4.1.3.0'
OID_RAMUSAGE = '1.3.6.1.4.1.12356.101.4.1.4.0'
OID_DISKUSAGE = '1.3.6.1.4.1.12356.101.4.1.6.0'
OID_DISKCAPACITY = '1.3.6.1.4.1.12356.101.4.1.7.0'

OID_SESSIONCOUNT = '1.3.6.1.4.1.12356.101.4.5.3.1.8'

OID_PERFORMANCESLALINKNAME = '1.3.6.1.4.1.12356.101.4.9.2.1.2'
OID_PERFORMANCESLALINKSTATE = '1.3.6.1.4.1.12356.101.4.9.2.1.4'
OID_PERFORMANCESLALINKLATENCY = '1.3.6.1.4.1.12356.101.4.9.2.1.5'
OID_PERFORMANCESLALINKJITTER = '1.3.6.1.4.1.12356.101.4.9.2.1.6'
OID_PERFORMANCESLALINKPACKETLOSS = '1.3.6.1.4.1.12356.101.4.9.2.1.9'
OID_PERFORMANCESLALINKBANDWIDTHIN = '1.3.6.1.4.1.12356.101.4.9.2.1.11'
OID_PERFORMANCESLALINKBANDWIDTHOUT = '1.3.6.1.4.1.12356.101.4.9.2.1.12'

OID_IFSTATUS = '1.3.6.1.2.1.2.2.1.8'
OID_IFNAME = '1.3.6.1.2.1.31.1.1.1.1'
OID_IFALIAS = '1.3.6.1.2.1.31.1.1.1.18'
OID_IFHCINOCTETS = '1.3.6.1.2.1.31.1.1.1.6'
OID_IFHCOUTOCTETS = '1.3.6.1.2.1.31.1.1.1.10'
