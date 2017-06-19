#
# A plugin to setup capture interfaces
# The plugin is off by default. To enable it, add "interfacesetup.enabled=1" to broctl.cfg.
#

import BroControl.plugin

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

        host_nodes = {}
        for n in nodes:
            if n.interface:
                host_nodes[(n.host, n.interface)] = n

        cmds = []
        for n in host_nodes.values():
            cmd = up_template.format(interface=n.interface, mtu=mtu)
            cmds.append((n, cmd))
            cmd = flags_template.format(interface=n.interface)
            cmds.append((n, cmd))

        for (n, success, output) in self.executeParallel(cmds):
            if not success:
                self.message("Failed to run command on {}:".format(n.host))
                self.message(output)
