# FortiGate Stats
Home Assistant integration to show statistics from a FortiGate firewall, via SNMP
- CPU, RAM and Disk usage
- Session count

To-do:
- Per-interface bandwidth usage sensors for user-selected interfaces 
- Estimated uplink bandwidth and health (if a performance SLA is enabled)

Tested and working with FortiOS 6.2.11 on a Fortigate 100D.

With thanks to [weltmeyer](https://github.com/weltmeyer) and [wxt9861](https://github.com/wxt9861) for doing 99% of the heavy lifting!

This is my first full Python hobbyist/testbed project and it's a work-in-progress... I'm sure there are many optimisations and improvements that could be made, feel free to comment.
