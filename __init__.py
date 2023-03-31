"""FortiGate Stats Integration."""
import asyncio
import logging
import os
from datetime import datetime, timedelta

#from .esxi import (
#    esx_connect,
#    esx_disconnect,
#    check_license,
#    get_host_info,
#    get_datastore_info,
#    get_license_info,
#    get_vm_info,
#    vm_pwr,
#    vm_snap_take,
#    vm_snap_remove,
#)

from .snmp import snmp_get
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST,
    CONF_USERNAME,
    CONF_PORT,
    CONF_MONITORED_CONDITIONS,
    __version__ as HAVERSION,    #check what this is for?
)
from homeassistant.util import Throttle

from .const import (
    DEFAULT_OPTIONS,
    DOMAIN,
    DOMAIN_DATA,
    PLATFORMS,
    REQUIRED_FILES,
)

_LOGGER = logging.getLogger(__name__)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

#VM_PWR_SCHEMA = vol.Schema(
#    {
#        vol.Required(HOST): cv.string,
#        vol.Required(VM): cv.string,
#        vol.Required(COMMAND): cv.string,
#    }
#)
#SNAP_CREATE_SCHEMA = vol.Schema(
#    {vol.Required(HOST): cv.string, vol.Required(VM): cv.string}, extra=vol.ALLOW_EXTRA
#)
#SNAP_REMOVE_SCHEMA = vol.Schema(
#    {
#        vol.Required(HOST): cv.string,
#        vol.Required(VM): cv.string,
#        vol.Required(COMMAND): cv.string,
#    }
#)
CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({}, extra=vol.ALLOW_EXTRA)}, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass, config):
    """Set up this integration using yaml.

    This method is no longer supported.
    """
    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    conf = hass.data.get(DOMAIN_DATA)
    if config_entry.source == config_entries.SOURCE_IMPORT:
        if conf is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
        # This is using YAML for configuration
        return False

    # check all required files
    file_check = await hass.async_add_executor_job(check_files, hass)
    if not file_check:
        return False

    config = {DOMAIN: config_entry.data}
    entry = config_entry.entry_id

    # create data dictionary
    if DOMAIN_DATA not in hass.data:
        hass.data[DOMAIN_DATA] = {}
    hass.data[DOMAIN_DATA][entry] = {}
    hass.data[DOMAIN_DATA][entry]["configuration"] = "config_flow"
    hass.data[DOMAIN_DATA][entry]["monitor_sdwan_interfaces"] = True #Temporary hard-coding
    hass.data[DOMAIN_DATA][entry]["monitor_session_count"] = True #Temporary hard-coding
    hass.data[DOMAIN_DATA][entry]["monitor_disk_usage"] = True #Temporary hard-coding
    hass.data[DOMAIN_DATA][entry]["monitor_cpu_ram"] = True #Temporary hard-coding
    hass.data[DOMAIN_DATA][entry]["monitored_sources"] = []

    if config_entry.data["monitor_sdwan_interfaces"]:
        hass.data[DOMAIN_DATA][entry]["monitored_sources"].append("sdwan_interfaces")
    if config_entry.data["monitor_session_count"]:
        hass.data[DOMAIN_DATA][entry]["monitored_sources"].append("session_count")
    if config_entry.data["monitor_disk_usage"]:
        hass.data[DOMAIN_DATA][entry]["monitored_sources"].append("disk_usage")
    if config_entry.data["monitor_cpu_ram"]:
        hass.data[DOMAIN_DATA][entry]["monitored_sources"].append("cpu_ram")
     
    if not config_entry.options:
        async_update_options(hass, config_entry)

    # get global config
    _LOGGER.debug("Setting up host %s", config[DOMAIN].get(CONF_HOST))
    hass.data[DOMAIN_DATA][entry]["client"] = snmpStats(hass, config, config_entry)

    # load platforms
    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    return True


#def connect(hass, config, entry):
#    """Connect."""
#    try:
#        conn_details = {f
#            "host": config[DOMAIN]["host"],
#            "user": config[DOMAIN]["username"],
#            "port": config[DOMAIN]["port"],
#        }
#        conn = esx_connect(**conn_details)  ## What's happening here?
#        _LOGGER.debug("Product Line: %s", conn.content.about.productLineId)#
#
#        hass.data[DOMAIN_DATA][entry]["client"].update_data()
#    except Exception as exception:  # pylint: disable=broad-except
#        _LOGGER.error(exception)
#        raise ConfigEntryNotReady
#    finally:
#        ##esx_disconnect(conn)
#
#    return lic


class snmpStats:
    """This class handles communication, services, and stores the data."""

    def __init__(self, hass, config, config_entry=None):
        """Initialize the class."""
        self.hass = hass
        self.config = config[DOMAIN]
        self.host = config[DOMAIN].get(CONF_HOST)
        self.user = config[DOMAIN].get(CONF_USERNAME)
        self.port = config[DOMAIN].get(CONF_PORT)
        self.entry = config_entry.entry_id

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update_data(self):
        """Update data."""
        try:
            # connect and get data from host
            self.hass.data[DOMAIN_DATA][self.entry]["serialnunber"] = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.100.1.1.1.0")
                    
        except Exception as error:
             _LOGGER.error("ERROR: %s", error)
        else:    
            if self.config.get("resource_usage") is True:
                # Get CPU and RAM resource usage info
                # CPU
                self.hass.data[DOMAIN_DATA][self.entry]["cpuusage"] = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.1.3.0")
                    
                # RAM
                self.hass.data[DOMAIN_DATA][self.entry]["ramusage"] = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.1.4.0")

                # Disk
                diskcapacity = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.1.7.0")
                diskusage = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.1.6.0")

                self.hass.data[DOMAIN_DATA][self.entry]["diskusage"] = (diskusage / diskcapacity) * 100
              
                
            if self.config.get("session_information") is True:
                # Get session info
                cpucount = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.5.2.0")

                currentcpu = 1
                sessioncount = 0
                while currentcpu < cpucount:
                    sessioncount += snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.5.3.1.8." + str(currentcpu))
                    currentcpu += 1
       
                self.hass.data[DOMAIN_DATA][self.entry]["sessioncount"] = sessioncount
                
                        
            if self.config.get("estimated_bandwidth") is True:
                # Get the estimated link bandwidth
                self.hass.data[DOMAIN_DATA][self.entry]["estimatedinboundbandwidth"] = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.9.2.1.11.1")
                self.hass.data[DOMAIN_DATA][self.entry]["estimatedoutboundbandwidth"] = snmp_get (self.host, self.user, self.port, "1.3.6.1.4.1.12356.101.4.9.2.1.12.1")


def check_files(hass):
    """Return bool that indicates if all files are present."""
    base = "{}/custom_components/{}/".format(hass.config.path(), DOMAIN)
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""
    if hass.data.get(DOMAIN_DATA, {}).get("configuration") == "yaml":
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
            )
        )
    else:
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
        _LOGGER.info("Successfully removed the FortiGate Stats integration")

    return True


@callback
def async_update_options(hass, config_entry):
    hass.config_entries.async_update_entry(config_entry, options=DEFAULT_OPTIONS)
