
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp

log = core.getLogger()

WHITELIST = ['10.0.0.1', '10.0.0.2']
MAC_TABLE = {}

class AccessController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        inport = event.ofp.in_port

        MAC_TABLE[packet.src] = inport

        arp_pkt = packet.find('arp')
        if arp_pkt:
            self._flood(event)
            return

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

def _handle_ConnectionUp(event):
    log.info("Switch %s has connected", event.dpid)

    # Allow h1 <-> h2 communication (ports 1 and 2)
    msg1 = of.ofp_flow_mod()
    msg1.match.in_port = 1
    msg1.actions.append(of.ofp_action_output(port=2))
    event.connection.send(msg1)

    msg2 = of.ofp_flow_mod()
    msg2.match.in_port = 2
    msg2.actions.append(of.ofp_action_output(port=1))
    event.connection.send(msg2)

    # Drop all other traffic
    drop = of.ofp_flow_mod()
    drop.priority = 0
    event.connection.send(drop)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)


