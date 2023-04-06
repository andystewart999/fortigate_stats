from pysnmp.entity.rfc3413.oneliner import cmdgen
import logging

LOGGER = logging.getLogger(__name__)

def snmp_get(host, user, port, oid):
    # connect and get data from host
    auth = cmdgen.CommunityData(user) ## More error trapping here!
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        auth, cmdgen.UdpTransportTarget((host, port)),
        cmdgen.MibVariable(oid),  
        lookupMib = False,
    )

    for oid, val in varBinds:
        value = val

    try:
        return errorIndication, int(value)
    except (ValueError, TypeError):
        try:
            return errorIndication, float(value)
        except (ValueError, TypeError):
            try:
                return errorIndication, str(value)
            except (ValueError, TypeError):
                pass
    return errorIndication, value


def snmp_getfromtable(host, user, port, oid):
    # connect and get data from host
    auth = cmdgen.CommunityData(user) ## More error trapping here!
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
        auth, cmdgen.UdpTransportTarget((host, port)),
        cmdgen.MibVariable(oid),  
        lookupMib = False,
    )
    
    return errorIndication, varTable 

 
def snmp_getmulti(host, user, port, oids):
    # connect and get data from host
    auth = cmdgen.CommunityData(user) ## More error trapping here!
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        auth, cmdgen.UdpTransportTarget((host, port)),
        *[cmdgen.MibVariable(oid) for oid in oids],  
        lookupMib = False,
    )

    return errorIndication, varBinds
