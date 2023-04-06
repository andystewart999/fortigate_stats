from pysnmp.entity.rfc3413.oneliner import cmdgen
import logging

_LOGGER = logging.getLogger(__name__)

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
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value


def snmp_getnext(host, user, port, oid):
    # connect and get data from host
    auth = cmdgen.CommunityData(user) ## More error trapping here!
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varTable = cmdGen.getNext(
        auth, cmdgen.UdpTransportTarget((host, port)),
        cmdgen.MibVariable(oid),  
        lookupMib = False,
    )
    
    return varTable 

 
def snmp_getmulti(host, user, port, oids):
    # connect and get data from host
    auth = cmdgen.CommunityData(user) ## More error trapping here!
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        auth, cmdgen.UdpTransportTarget((host, port)),
        *[cmdgen.MibVariable(oid) for oid in oids],  
        lookupMib = False,
    )

    return varBinds
