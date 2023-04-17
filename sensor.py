import time
import traceback
import asyncio
#import sys

# pylint: disable=unused-wildcard-import
from .const import * 
from .snmp import snmp_getfromtable, snmp_getmulti, snmp_getmultifromtable

# pylint: enable=unused-wildcard-import
import threading
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    EVENT_HOMEASSISTANT_STOP, 
    CONF_SCAN_INTERVAL,
    CONF_PORT
)


async def async_setup_entry(hass, config_entry,async_add_entities):
    """Set up the sensor platform."""
    maxretries=3
    
    for i in range(maxretries):
        try:
            monitor = SnmpStatisticsMonitor(config_entry,async_add_entities)
            break
        except:
            if i==maxretries-1:
                raise
       
    hass.data[DOMAIN][config_entry.entry_id]={"monitor":monitor}

    ### TESTING ###
    # load platforms
    for platform in PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )
    ### TESTING ###

    
    monitor.start()
    
    def _stop_monitor(_event):
        monitor.stopped=True
        #hass.states.async_set
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, _stop_monitor)
        LOGGER.info('Init done')
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
    LOGGER.info("Successfully removed the FortiGate Stats integration")

    return True
### TESTING ###


class SnmpStatisticsSensor(Entity):
    def __init__(self,id,fw_info,name=None,unit=None,icon=None):
        self._attributes = {}
        self._state ="NOTRUN"
        self.fw_info = fw_info
        self.entity_id=id
        if name is None:
            name=id
        self._name=name
        if unit is not None:
            self._unitofmeasurement=unit
        if icon is None:
            icon = "mdi:eye"
        self._icon = icon
            
        LOGGER.info("Created sensor {0}".format(id))

    def set_state(self, state):
        """Set the state."""
        if self._state==state:
            return
        self._state = state
        if self.enabled:
            self.schedule_update_ha_state()

    def set_attributes(self, attributes):
        """Set the state attributes."""
        self._attributes = attributes

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        return self._icon

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return self.entity_id

    @property
    def should_poll(self):
        """Only poll to update phonebook, if defined."""
        return False
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unitofmeasurement
    @property
    def state(self):
        """Return the state of the device."""
        return self._state
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    def update(self):
        LOGGER.info("Updated "+self.entity_id)

    @property
    def device_info(self):
        """Return device info for this sensor."""
        identifier = {(DOMAIN, self.fw_info[OID_SERIALNUMBER])}
        return {
            "identifiers": identifier,
            "name": self.fw_info[OID_HOSTNAME],
            "manufacturer": "Fortinet",
            "model": self.fw_info[OID_MODEL],
            "sw_version": self.fw_info[OID_FORTIOS]
        }

class SnmpStatisticsMonitor:

    def __init__(self,config_entry,async_add_entities=None):
        self.meterSensors={}
        self.stopped = False
        self.async_add_entities=async_add_entities
        self.current_if_data={} 
        self.current_if_data_time=0
        self.stat_time=0
        self.username=config_entry.data.get(CONF_USERNAME)
        self.target_ip=config_entry.data.get(CONF_IP_ADDRESS)
        self.port=config_entry.data.get(CONF_PORT)
        self.updateIntervalSeconds=config_entry.data.get(CONF_SCAN_INTERVAL)
        self.include_cpu_and_ram=config_entry.data.get(CONF_CPUANDRAM)
        self.include_disk=config_entry.data.get(CONF_DISK)
        self.include_sessions=config_entry.data.get(CONF_SESSIONS)

        self.include_interfaces = config_entry.data.get(CONF_INTERFACESYESNO)
        if self.include_interfaces:
            self.interfaces = config_entry.data.get(CONF_INTERFACES)
            self.interfacesbandwidth = config_entry.data.get(CONF_INTERFACESBANDWIDTH)
            self.interfacesoctets = config_entry.data.get(CONF_INTERFACESOCTETS)

        self.include_performanceslas = config_entry.data.get(CONF_PERFORMANCESLASYESNO)
        if self.include_performanceslas:
            self.performance_slas = config_entry.data.get(CONF_PERFORMANCESLAS)
            self.include_performanceslasstate = config_entry.data.get(CONF_PERFORMANCESLASSTATE)
            self.include_performanceslaslinkmetrics = config_entry.data.get(CONF_PERFORMANCESLASLINKMETRICS)
            self.include_performanceslasbandwidthprobe = config_entry.data.get(CONF_PERFORMANCESLASBANDWIDTHPROBE)
          
        self.fw_info = {
            OID_HOSTNAME: config_entry.data.get(OID_HOSTNAME),
            OID_SERIALNUMBER: config_entry.data.get(OID_SERIALNUMBER),
            OID_MODEL: config_entry.data.get(OID_MODEL),
            OID_FORTIOS: config_entry.data.get(OID_FORTIOS)
            }
        self.update_stats()#try this to throw error if not working.
        if async_add_entities is not None:
            self.setupEntities()

    def update_stats(self):
        self.update_netif_stats()
        
    def update_netif_stats(self):
        if_data=self.current_if_data
 
        oids = (OID_IFNAME, OID_IFALIAS, OID_IFHCINOCTETS, OID_IFHCOUTOCTETS) 
        errorIndication, snmp_data = snmp_getmultifromtable(self.target_ip, self.username, self.port, oids)
        if not errorIndication:

            for interface in if_data:
                if_data[interface]['rx_octets_prev'] = if_data[interface]['rx_octets']
                if_data[interface]['tx_octets_prev'] = if_data[interface]['tx_octets']

            for if_name, if_alias, if_hcinoctets, if_hcoutoctets in snmp_data:
                if if_name[0].prettyPrint() in self.interfaces:
                    #The interface is in scope.
                        
                    ifId = if_name[0].prettyPrint()
                    if ifId not in if_data:
                        if_data[ifId]={
                            'name':'',
                            'alias':'',
                            'rx_octets':-1,
                            'tx_octets':-1,
                            'rx_speed_octets':-1.0,
                            'tx_speed_octets':-1.0,
                            'rx_octets_prev':-1.0,
                            'tx_octets_prev':-1.0,
                            'last_stat_time':time.time(),
                            'rx_diff':-1,
                            'tx_diff':-1
                            }
                
                    if_data[ifId]['name'] = if_name[1].prettyPrint()
                    if_data[ifId]['alias'] = if_alias[1].prettyPrint()
                    if_data[ifId]['rx_octets'] = int(if_hcinoctets[1].prettyPrint())
                    if_data[ifId]['tx_octets'] = int(if_hcoutoctets[1].prettyPrint())

            new_if_data_time=time.time()
            for k in self.current_if_data:
                cur_data=self.current_if_data[k]
                
                timediff_statistics=new_if_data_time-cur_data['last_stat_time']
                timediff_stat_seconds=timediff_statistics#/1000.0

                rx_diff=cur_data['rx_octets'] - cur_data['rx_octets_prev']
                tx_diff=cur_data['tx_octets'] - cur_data['tx_octets_prev']

                cur_data['rx_diff']=rx_diff
                cur_data['tx_diff']=tx_diff

                if timediff_stat_seconds<1:
                    continue

                if rx_diff==0 and tx_diff==0 and timediff_stat_seconds<4:##wait until really going to 0
                    continue

                rx_byte_s = rx_diff / timediff_stat_seconds
                tx_byte_s = tx_diff / timediff_stat_seconds
                cur_data['last_stat_time']=new_if_data_time

                cur_data['rx_speed_octets']=rx_byte_s
                cur_data['tx_speed_octets']=tx_byte_s


            self.current_if_data=if_data
            self.current_if_data_time=new_if_data_time

    def start(self):
        threading.Thread(target=self.watcher).start()
    def watcher(self):
        LOGGER.info(f'Start Watcher Thread - updateInterval:{self.updateIntervalSeconds}')

        while not self.stopped:
            try:
                self.update_stats()
                if self.async_add_entities is not None:
                    self.AddOrUpdateEntities()
            except (KeyError,PySnmpError):
                time.sleep(1)
            except:
                e = traceback.format_exc()
            if self.updateIntervalSeconds is None:
                self.updateIntervalSeconds=DEFAULT_SCAN_INTERVAL

            time.sleep(self.updateIntervalSeconds)

    #region HA
    def setupEntities(self):
        self.update_stats()
        
        if self.async_add_entities is not None:
            self.AddOrUpdateEntities()

    
    def _AddOrUpdateEntity(self,id,friendlyname,value,unit,icon,attributes = None):
        if id in self.meterSensors:
            sensor=self.meterSensors[id]
            sensor.set_state(value)
        else:
            sensor=SnmpStatisticsSensor(id,self.fw_info,friendlyname,unit,icon)
            sensor._state=value
            self.async_add_entities([sensor])
            self.meterSensors[id]=sensor
            
        if attributes is not None:
            sensor.set_attributes (attributes)
        
    def AddOrUpdateEntities(self):
        allSensorsPrefix = "sensor." + DOMAIN + "_" + self.fw_info[OID_SERIALNUMBER].replace('.','_') + "_"
        
        for k in self.current_if_data:
            cur_if_data=self.current_if_data[k]
            if_name=cur_if_data['name']
            if_alias=cur_if_data['alias']
            
            if if_alias != "":
                if_display = if_alias
            else:
                if_display = if_name
 
            if_rx_mbit=cur_if_data['rx_speed_octets']*8/1000/1000
            if_tx_mbit=cur_if_data['tx_speed_octets']*8/1000/1000
            #if_rx_mbyte=cur_if_data['rx_speed_octets']/1000/1000
            #if_tx_mbyte=cur_if_data['tx_speed_octets']/1000/1000

            # if_rx_total_mbit=cur_if_data['rx_octets']*8/1000/1000
            # if_tx_total_mbit=cur_if_data['tx_octets']*8/1000/1000

            if self.interfacesbandwidth:
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_out_mbit',if_display+" bandwidth out",round(if_tx_mbit,2),'Mbps',"mdi:upload-network-outline")
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_in_mbit',if_display+" bandwidth in",round(if_rx_mbit,2),'Mbps',"mdi:download-network-outline")

            if self.interfacesoctets:
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_octets_out',if_display+" octets out",int(cur_if_data['tx_octets']),'octets',"mdi:upload-network-outline")
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_octets_in',if_display+" octets in",int(cur_if_data['rx_octets']),'octets',"mdi:download-network-outline")

            #self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_out_mbyte',if_name+" BW Out (mbyte)",round(if_tx_mbyte,2),'mbyte/s')
            #self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_in_mbyte',if_name+" BW In (mbyte)",round(if_rx_mbyte,2),'mbyte/s')

            # self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_out_mbit',if_name+" Total Out (mbit)",round(if_tx_total_mbit,2),'mbit')
            # self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_in_mbit',if_name+" Total In (mbit)",round(if_rx_total_mbit,2),'mbit')
            
            # self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_out_byte',if_name+" Total Out (bytes)",cur_if_data['tx_octets'],'byte')
            # self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_in_byte',if_name+" Total In (bytes)",cur_if_data['rx_octets'],'byte')

        if self.include_cpu_and_ram:
            oids = (OID_CPUUSAGE, OID_RAMUSAGE)
            errorIndication, oidReturn = snmp_getmulti(self.target_ip, self.username, self.port, oids)

            if not errorIndication:
                cpu_usage = int(oidReturn[0][1].prettyPrint())
                ram_usage = int(oidReturn[1][1].prettyPrint())

                self._AddOrUpdateEntity(allSensorsPrefix+"cpu_usage","CPU usage",cpu_usage,'%',"mdi:memory")
                self._AddOrUpdateEntity(allSensorsPrefix+"ram_usage","RAM usage",ram_usage,'%',"mdi:memory")

        if self.include_disk:
            oids = (OID_DISKUSAGE, OID_DISKCAPACITY)
            errorIndication, oidReturn = snmp_getmulti(self.target_ip, self.username, self.port, oids)
            
            if not errorIndication:
                disk_usage = int(oidReturn[0][1].prettyPrint())
                disk_capacity = int(oidReturn[1][1].prettyPrint())

                disk_usagepct = int((disk_usage / disk_capacity) * 100)
                disk_attrs = (
                    {
                        "Disk capacity (MB)":disk_capacity,
                        "Disk usage (MB)":disk_usage
                    }
                )
                self._AddOrUpdateEntity(allSensorsPrefix+"disk_usage","Disk usage",disk_usagepct,'%',"mdi:database", disk_attrs)

        if self.include_sessions:
            errorIndication, snmp_data = snmp_getfromtable(self.target_ip, self.username, self.port, OID_SESSIONCOUNT)
            
            sessioncount = 0
            if not errorIndication:
                for oid_entry in snmp_data:
                    for oid, oid_value in oid_entry:
                        sessioncount += int(oid_value.prettyPrint())
            
                self._AddOrUpdateEntity(allSensorsPrefix+"sessions","Sessions",sessioncount,'sessions',"mdi:format-list-bulleted-type")
            
        if self.include_performanceslas:
            oids = (OID_PERFORMANCESLALINKNAME, OID_PERFORMANCESLALINKSTATE, OID_PERFORMANCESLALINKLATENCY, OID_PERFORMANCESLALINKJITTER, OID_PERFORMANCESLALINKPACKETLOSS, OID_PERFORMANCESLALINKBANDWIDTHIN, OID_PERFORMANCESLALINKBANDWIDTHOUT) 

            errorIndication, snmp_data = snmp_getmultifromtable(self.target_ip, self.username, self.port, oids)
            if not errorIndication:
                for sla_name, sla_state, sla_latency, sla_jitter, sla_packetloss, sla_bandwidthin, sla_bandwidthout in snmp_data:
                    if sla_name[0].prettyPrint() in self.performance_slas:
                        #The performance SLA itself is in scope.  See what we should be creating sensors for
                        sla_index = sla_name[0].prettyPrint().split(".")[-1]
                        sla_name = sla_name[1].prettyPrint()
                        sla_state = sla_state[1].prettyPrint()
                        
                        if self.include_performanceslasstate:
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_state_" + sla_index, sla_name + " state",PERFORMANCESLAS_STATE[sla_state],'',PERFORMANCESLAS_ICON[sla_state])
                        
                        if self.include_performanceslaslinkmetrics:
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_latency_" + sla_index, sla_name + " latency",int(float(sla_latency[1].prettyPrint())),'ms',"mdi:timeline-clock-outline")
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_jitter_" + sla_index, sla_name + " jitter",int(float(sla_jitter[1].prettyPrint())),'ms',"mdi:timeline-clock-outline")
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_packetloss_" + sla_index, sla_name + " packet loss",int(float(sla_packetloss[1].prettyPrint())),'%',"mdi:timeline-alert-outline")
              
                        if self.include_performanceslasbandwidthprobe:
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_bandwidthin_" + sla_index, sla_name + " probe bandwidth (in) ",int(sla_bandwidthin[1].prettyPrint())/1000,'Mbps',"mdi:download-network-outline")
                            self._AddOrUpdateEntity(allSensorsPrefix+"sla_bandwidthout_" + sla_index, sla_name + " probe bandwidth (out) ",int(sla_bandwidthout[1].prettyPrint())/1000,'Mbps',"mdi:upload-network-outline")
                        
