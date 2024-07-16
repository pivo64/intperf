# Interface Performance Monitor for Cisco Nexus NX-OS Switches >> intperf <<

This Python script is designed to be executed directly on a Cisco NEXUS switch. 

Tested on following Nexus switches
 - 5672UP with NX-OS 7.3(7)
 - C93180YC-EX with NX-OS 9.3(8)
 - C93180YC-FX with NX-OS 10.2(7)
 - C9336C-FX2 with NX-OS 9.3(8)

## Installation
Copy the file `intperf.py` to the `bootflash:scripts/` directory. Than configure a command alias:

* on Nexus 5000:
  `cli alias name intperf source intperf.py`
* on Nexus 9000:
  `cli alias name intperf python bootflash:scripts/intperf.py`
 
## Description
Shows a live view for in/out-throughput of given single interface, a interface range
or a list of interfaces on terminal.
Supported Interface Types are:
 - Ethernet: e1/1 eth2/2-4 ...
 - Ethernet on Fex: e101/1/1-40 eth104/1/5-10 ...
 - Port-Channels: port-channel1, po2 ...

The view refresh automatically every 5 seconds.

## Using
positional arguments:
  `Interface or Interface-list`

optional arguments:
```
  -h, --help            show this help message and exit
  -i 5-3600, --interval 5-3600
  -l [logfile], --logfile [logfile]
```

Examples:
```
# intperf e1/1-8 e101/1/25-40 po101
    Int     : Speed and State : Description         : Mbps in    : Mbps out   :
Eth1/1      : 40 Gb/s    up   : FEX101_FX1          :      184.4 :      343.0 :
Eth1/2      : 40 Gb/s    up   : FEX101_FX2          :      101.6 :      209.8 :
Eth1/3      : 40 Gb/s    up   : FEX201_FX1          :      174.6 :      189.1 :
Eth1/4      : 40 Gb/s    up   : FEX201_FX2          :      178.8 :      308.3 :
Eth1/5      : 40 Gb/s    up   : FEX301_FX1          :      472.2 :      291.2 :
Eth1/6      : 40 Gb/s    up   : FEX301_FX2          :      454.8 :      248.9 :
Eth1/7      : 40 Gb/s    up   : FEX401_FX1          :      161.1 :      146.0 :
Eth1/8      : 40 Gb/s    up   : FEX401_FX2          :       64.6 :      159.9 :
Eth101/1/25 : 10 Gb/s    up   : SERVER1_eth1/2      :        3.2 :        3.5 :
Eth101/1/26 : 10 Gb/s    up   : SERVER1_eth1/1      :       40.1 :       39.8 :
Eth101/1/27 : 10 Gb/s    up   : SERVER2_eth1/2      :        3.2 :       44.9 :
Eth101/1/28 : 10 Gb/s    up   : SERVER2_eth1/1      :       15.3 :       32.3 :
Eth101/1/29 : 10 Gb/s    up   : SERVER3_eth1/2      :        3.2 :       12.0 :
Eth101/1/30 : 10 Gb/s    up   : SERVER3_eth1/1      :        9.9 :       33.3 :
Eth101/1/31 : 10 Gb/s    up   : SERVER4_eth1/2      :       30.3 :       27.3 :
Eth101/1/32 : 10 Gb/s    up   : SERVER4_eth1/1      :       10.3 :       13.2 :
Eth101/1/33 : 10 Gb/s    up   : SERVER5_eth1/2      :        0.0 :        0.0 :
Eth101/1/34 : 10 Gb/s    up   : SERVER5_eth1/1      :        0.0 :        0.0 :
Eth101/1/35 : 10 Gb/s    up   : SERVER6_eth1/2      :        0.0 :        0.0 :
Eth101/1/36 : 10 Gb/s    up   : SERVER6_eth1/1      :        0.0 :        0.0 :
Eth101/1/37 : 10 Gb/s    up   : SERVER7_eth1/2      :        0.0 :        0.0 :
Eth101/1/38 : 10 Gb/s    up   : SERVER7_eth1/1      :        0.0 :        0.0 :
Eth101/1/39 : 10 Gb/s    up   : SERVER8_eth1/2      :        0.0 :        0.0 :
Eth101/1/40 : 10 Gb/s    up   : SERVER8_eth1/1      :        0.0 :        0.0 :
Po101       : 40 Gb/s    up   : FEX101              :      305.2 :      548.0 :
interval  7s - Last Update: 13:53:39 - Exec Time 3.98 - Press "Q" to end
```

Hint:
  If the output seems corrupt with unnecessary new-lines, try:
    
  `# terminal lenght 0`
  
  before intperf start.
