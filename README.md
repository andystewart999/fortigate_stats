# FortiGate Stats
Home Assistant integration to show statistics from a FortiGate firewall, via SNMP
- CPU, RAM and Disk usage
- Session count
- Performance SLA/Link Health status (if enabled on the firewall)
- Per-interface bandwidth usage sensors for connected interfaces 

TODO:
- Work out how to support removal of this integration without requiring Home Assistant to restart
- Work out how to support integration reloading

Tested and working with FortiOS 6.2.11 on a Fortigate 100D.

With thanks to [weltmeyer](https://github.com/weltmeyer) and [wxt9861](https://github.com/wxt9861) for doing most of the heavy lifting!

This is my first full Python hobbyist/testbed project and it's a work-in-progress... I'm sure there are many optimisations and improvements that could be made, feel free to comment.
