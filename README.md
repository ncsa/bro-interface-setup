# Bro Interface Setup

A broctl plugin that helps you setup capture interfaces.

## Configuration

The plugin is off by default. To enable it, add "interfacesetup.enabled=1" to broctl.cfg.

### broctl.cfg example

```
interfacesetup.enabled=1
#To change the default mtu that is configured
#interfacesetup.mtu=9000

#To change the default commands that are used to bring up the interface
#interfacesetup.up_command=/sbin/ifconfig {interface} up mtu {mtu}
#interfacesetup.flags_command=/sbin/ethtool -K {interface} gro off lro off rx off tx off gso off
```
