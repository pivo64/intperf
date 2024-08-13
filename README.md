# Interface Performance Monitor for Cisco Nexus NX-OS Switches >> intperf <<

This Python script is designed to be executed directly on a Cisco NEXUS switch. 

Tested on following Nexus switches
 - 5672UP with NX-OS 7.3(7)
 - C92348GC-X NX-OS 10.2(7)
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
# intperf e1/1-8 e101/1/24-34 po1 po101
BSY Int     : Speed and State : Description         : Mbps in    : Mbps out   :
Eth1/1      :   40 Gb/s  up   : PFEX101_FX1         :      504.2 :      383.5 :
Eth1/2      :   40 Gb/s  up   : PFEX101_FX2         :      200.0 :      224.0 :
Eth1/3      :   40 Gb/s  up   : PFEX201_FX1         :      756.9 :      412.0 :
Eth1/4      :   40 Gb/s  up   : PFEX201_FX2         :      313.0 :      731.6 :
Eth1/5      :   40 Gb/s  up   : PFEX301_FX1         :      703.7 :      590.6 :
Eth1/6      :   40 Gb/s  up   : PFEX301_FX2         :      583.2 :      908.0 :
Eth1/7      :   40 Gb/s  up   : PFEX401_FX1         :      665.0 :      202.8 :
Eth1/8      :   40 Gb/s  up   : PFEX401_FX2         :       82.2 :      217.7 :
Eth101/1/24 :   10 Gb/s  down : MGMT-Outlet         :        0.0 :        0.0 :
Eth101/1/25 :   10 Gb/s  up   : ASRV101_E8/2        :      109.2 :      121.1 :
Eth101/1/26 :   10 Gb/s  up   : ASRV101_E2/1        :       19.8 :       22.2 :
Eth101/1/27 :   10 Gb/s  up   : ASRV102_E8/2        :        3.3 :       65.4 :
Eth101/1/28 :   10 Gb/s  up   : ASRV102_E2/1        :       11.9 :       19.9 :
Eth101/1/29 :   10 Gb/s  up   : ASRV103_E8/2        :       71.1 :       56.8 :
Eth101/1/30 :   10 Gb/s  up   : ASRV103_E2/1        :        8.2 :        7.3 :
Eth101/1/31 :   10 Gb/s  up   : ASRV104_E8/2        :        3.1 :        3.1 :
Eth101/1/32 :   10 Gb/s  up   : ASRV104_E2/1        :       34.7 :       43.0 :
Eth101/1/33 :   10 Gb/s  up   : ASRV105_E8/2        :        5.1 :        4.2 :
Eth101/1/34 :   10 Gb/s  up   : ASRV105_E2/1        :        7.3 :       42.6 :
Po1         :  200 Gb/s  up   : SWITA011_Po1         :      637.2 :      559.8 :
Po101       :   80 Gb/s  up   : PFEX101             :      512.0 :      252.7 :
interval  5s - Last Update: 13:49:36 - Exec Time 3.47 - Press "Q" to end
```

Hint:
  If the output seems corrupt with unnecessary new-lines, try:
    
  `# terminal lenght 0`
  
  before intperf start.

### Interval
The terminal refresh interval starts with 5 seconds. If the 'Exec Time' (the time for the 'show interface' command which is uses by this script) exceeds the 5 seconds, the interval increases by 2 seconds.

The initial interval can be set with the `-i nn` or `--interval nn` optional parameter.

### Error Counter
With the option `-e` or `--error` you will get two additional columns with intput- and output errors of the interfaces. 

### Logfile
You can write a optional logfile in '.csv' style with the parameter `-l filename`  or `--logfile filename`. If you put this parameter on last position, you can omit the 'filename'. The logfile name is then `ìntperf.csv` on `bootflash:`.

### Screen refresh
Resizing the screen while the program is running can lead to a corrupted screen (the content is only partially displayed). In this case, press the 'r' button to force a screen refresh.

### Ending the Program
The program ends when you press the 'q' key. It is possible that the program continues to run for a few seconds, depending on the execution time of the internal CLI command. 
