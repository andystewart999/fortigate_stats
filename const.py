"""Constants for FortiGate Stats."""
DOMAIN = "fortigate_stats"
DOMAIN_DATA = "{}_data".format(DOMAIN)

PLATFORMS = ["sensor"]
REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "sensor.py",
    "config_flow.py",
    "translations/en.json",
]
VERSION = "0.1.0"
ISSUE_URL = "https://github.com/andystewart999/fortigate_stats/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

CONF_NAME = "name"
#CONF_DS_STATE = "datastore"
#CONF_HOST_STATE = "vmhost"
#CONF_LIC_STATE = "license"
#CONF_VM_STATE = "vm"

DEFAULT_NAME = "FortiGate stats"
DEFAULT_PORT = 161
#DEFAULT_DS_STATE = "free_space_gb"
#DEFAULT_HOST_STATE = "vms"
#DEFAULT_LIC_STATE = "status"
#DEFAULT_VM_STATE = "state"

## used to set default states for yaml config.
DEFAULT_OPTIONS = {
    "resource_usage": True,
    "session_information": True,
    "estimated_bandwidth": True
}

#DATASTORE_STATES = [
#    "connected_hosts",
#    "free_space_gb",
#    "total_space_gb",
#    "type",
#    "virtual _machines",
#]

#LICENSE_STATES = [
#    "expiration_days",
#    "status"
#]

#VMHOST_STATES = [
#    "cpuusage_ghz",
#    "memusage_gb",
#    "state",
#    "uptime_hours",
#    "vms"
#]

#VM_STATES = [
#    "cpu_use_pct",
#    "memory_used_mb",
#    "snapshots",
#    "status",
#    "state",
#    "uptime_hours","
#    "used_space_gb"
#]

SNMP_MAP = {
    "1.3.6.1.4.1.12356.101.4.1.1.0": "FortiOS version",
    "1.3.6.1.4.1.12356.101.4.1.3.0": "CPU usage (%)",
    "1.3.6.1.4.1.12356.101.4.1.4.0": "Memory usage (%)",
    "1.3.6.1.4.1.12356.101.4.1.6.0": "Disk usage (MB)",
    "1.3.6.1.4.1.12356.101.4.1.7.0": "Disk capacity (MB)", # We need both of these to get a percentage, SNMP won't return it directly
    "1.3.6.1.4.1.12356.101.4.5.2.0": "Processor module count",
    "1.3.6.1.4.1.12356.101.4.5.3.1.8": "Sessions", # Append with .1, ,2 etc depending on the processor module count, then sum all the values
    "1.3.6.1.4.1.12356.101.4.9.1.0": "SD-WAN health check count",
    "1.3.6.1.4.1.12356.101.4.9.2.1.2": "SD-WAN health check name", # All the health check OIDs need to be appended with .1, .2 etc depending on the health check count
    "1.3.6.1.4.1.12356.101.4.9.2.1.4": "SD-WAN health check state",
    "1.3.6.1.4.1.12356.101.4.9.2.1.5": "SD-WAN health check latency",
    "1.3.6.1.4.1.12356.101.4.9.2.1.9": "SD-WAN health check packet loss",
    "1.3.6.1.4.1.12356.101.4.9.2.1.11": "SD-WAN health check inbound bandwidth (estimated)",
    "1.3.6.1.4.1.12356.101.4.9.2.1.12": "SD-WAN health check outbound bandwidth (estimated)",
    "1.3.6.1.4.1.12356.101.4.9.2.1.14": "SD-WAN health check interface name"
}

SUPPORTED_PRODUCTS = ["FortiGate", "FortiGate"]
