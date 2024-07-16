# Interface Performance Monitor for Cisco Nexus NX-OS Switches >> intperf <<

Tested on following Nexus switches
 - 5672UP with NX-OS 7.3(7)
 - C93180YC-EX with NX-OS 9.3(8)
 - C93180YC-FX with NX-OS 10.2(7)
 - C9336C-FX2 with NX-OS 9.3(8)
 
## Description
Shows a live view for in/out-throughput of given single interface, a interface range
or a list of interfaces on terminal.
Supported Interface Types are:
 - Ethernet: e1/1 eth2/2-4 ...
 - Ethernet on Fex: e101/1/1-40 eth104/1/5-10 ...
 - Port-Channels: port-channel1, po2 ...

The view refresh automatically every 5 seconds.
