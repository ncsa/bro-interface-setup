#
# A plugin to setup capture interfaces
# The plugin is off by default. To enable it, add "interfacesetup.enabled=1" to broctl.cfg.
#

import BroControl.plugin

def extract_interfaces(intf):
    #Handle interfaces that look like multi:p1p1,p1p2
    if intf.startswith("pf_ring::multi:"):
        return intf.replace("pf_ring::multi:", "").split(",")
    #Handle interfaces that look like myricom::p1p1:4
    if '::' in intf:
        intf = intf.split('::')[1]
    if ':' in intf:
        intf = intf.split(':')[0]
    return intf.split(',')

class InterfaceSetupPlugin(BroControl.plugin.Plugin):
    def __init__(self):
        super(InterfaceSetupPlugin, self).__init__(apiversion=1)

    def name(self):
        return "InterfaceSetupPlugin"

    def prefix(self):
        return "interfacesetup"

    def pluginVersion(self):
        return 1

    def init(self):
        if self.getOption("enabled") == "0":
            return False

        return True

    def options(self):
        return [("mtu", "int", 9216, "Interface MTU"),
                ("enabled", "string", "0", "Set to enable plugin"),
                ("up_command", "string", "/sbin/ifconfig {interface} up mtu {mtu}", "Command to bring the interface up"),
                ("flags_command", "string", "/sbin/ethtool -K {interface} gro off lro off rx off tx off gso off", "Command to setup the interface for capturing"),
        ]

    def cmd_start_pre(self, nodes):
        if not nodes:
            return
        
        mtu = self.getOption("mtu")
        up_template = self.getOption("up_command")
        flags_template = self.getOption("flags_command")
        self.message("InterfaceSetupPlugin: bringing up interfaces with an mtu of %s" % (mtu))

        host_interfaces = {}
        for n in nodes:
            intf = n.interface
            if not intf:
                continue
            if '*' in intf:
                self.error("Interface setup can't handle wildcard interfaces")
                continue
            for intf in extract_interfaces(intf):
                host_interfaces[(n.host, intf)] = (n, intf)

        cmds = []
        for (n, intf) in host_interfaces.values():
            cmd = up_template.format(interface=intf, mtu=mtu)
            cmds.append((n, cmd))
            cmd = flags_template.format(interface=intf)
            cmds.append((n, cmd))

        for (n, success, output) in self.executeParallel(cmds):
            if not success:
                self.message("Failed to run command on {}:".format(n.host))
                self.message(output)
