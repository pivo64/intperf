#!/usr/bin/env python
#
# Program: intperf
#   shows throughput of physical interfaces on device
#
# MIT License
#
# Copyright (c) 2024 Pietro Volante (pietro_volante@online.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
VERSION = '3.4b'
VERSION_DATE = '19.08.2024'
DESCRIPTION='''
Shows a live view for in/out-throughput of given single interface, a interface range
or a list of interfaces on terminal.
Supported Interface Types are:
 - Ethernet:        e1/1 eth2/2-4 ...
 - Ethernet on Fex: e101/1/1-40 eth104/1/5-10 ...
 - Port-Channels:   port-channel1, po2, po104 ...

The view refresh automatically (5sec default refresh time).
'''
EPILOG = '''
Examples: 
  # intperf e1/1 e101/1/25-40 po1 po3
  # intperf --logfile mylog.csv eth102/1/15-40 po102
  # intperf --interval 10 e1/1-48 po1 --logfile

Hint: 
  If the output seems corrupt with unnecessary new-lines, try:
    # terminal length 0
  before starting intperf.

Version: {} - Date: {}
'''.format(VERSION, VERSION_DATE)

# simulation mode allows program execution outsite Nexus platform
global SIM
#SIM = True
SIM = False

if SIM:
    from interface_test import intf
else:
    if 'clid' in dir():
        # set clid call function for N5k
        run_cli = clid
    else:
        # import cli for n9k
        import cli
        run_cli = cli.clid

import json
import time
import argparse
import re
import curses
from curses import wrapper

# constants
global INTERVAL_ADD
INTERVAL_ADD = 2.0
global FACTOR
FACTOR = 1000000.0
global FACTORSTR
FACTORSTR = 'Mbps'

#--------------------
class InterfaceStats:
    '''
    Class to collect interface counter statistics and calculates 
    the throughput of each interface
    '''
    def __init__(self, int_list_str):
        self.int_list_str = int_list_str
        self._first_run = True
        self.exec_time = 0.0
        self.output_list = []
        self.int_list = []
        self.interfaces = {}
        self.int_list_valid = True

        # validate interface list with simple commande 'show interface description'
        if SIM:  #- Simulation mode
            cmdinput = intf
            self.int_list_valid = True
        else:
            try:
                cmdinput = run_cli('show interface {} description'.format(self.int_list_str))
            except:
                print('command "show interface {} description" failed'.format(self.int_list_str))
                self.int_list_valid = False
                return

            cmdinput = json.loads(cmdinput)

        if self.int_list_valid:
            # create validate interface list
            output_list = cmdinput['TABLE_interface']['ROW_interface']
            
            if isinstance(output_list, dict):
                # single interface 
                self.int_list = [ output_list['interface'] ]
                self.int_len = 1
            else:
                # multiple interfaces
                self.int_len = len(output_list)
                self.int_list = \
                    [output_list[n]['interface'] for n in range(self.int_len)]

    def get_stat(self):
        # check if interface list already 
        # collect interface data and calulate results
        int_dict = {}

        # calulate delta time
        if self._first_run:
            self.delta_time = 1.0
        else:
            # calculate time since last command execution
            self.delta_time = time.time() - self.timestamp
        self.timestamp = time.time()

        # cli command execution
        if SIM:
            cmdinput = intf
        else:
            cmdinput = json.loads(run_cli('show interface {}'.format(self.int_list_str)))

        # test if result are multiple or single interfaces
        if isinstance(cmdinput['TABLE_interface']['ROW_interface'], dict):
            # single interface - convert to list
            self.output_list = [cmdinput['TABLE_interface']['ROW_interface']]
        else:
            self.output_list = cmdinput['TABLE_interface']['ROW_interface']
        
        # calculate results for each interface in list
        for data in self.output_list:
            int_name  = data.get('interface', '')
            # prepare dict with collected data
            if self._first_run:
                # at first run no throutput data
                int_dict['in_bytes'] = float(data.get('eth_inbytes', '0'))
                int_dict['out_bytes'] = float(data.get('eth_outbytes', '0'))
                int_dict['in_bytes-1'] = 0.0
                int_dict['out_bytes-1'] = 0.0
                int_dict['in_tput'] = 0.0
                int_dict['out_tput'] = 0.0
            else:
                # store old byte counters
                int_dict['in_bytes-1'] = self.interfaces[int_name]['in_bytes']
                int_dict['out_bytes-1'] = self.interfaces[int_name]['out_bytes']
                # get new byte counters
                int_dict['in_bytes'] = float(data.get('eth_inbytes', '0'))
                int_dict['out_bytes'] = float(data.get('eth_outbytes', '0'))
                # calculate throughput
                int_dict['in_tput'] = \
                    (int_dict['in_bytes'] - int_dict['in_bytes-1']) \
                        * 8.0 / self.delta_time / FACTOR
                int_dict['out_tput'] = \
                    (int_dict['out_bytes'] - int_dict['out_bytes-1']) \
                    * 8.0 / self.delta_time / FACTOR

            int_dict['description'] = data.get('desc', '')
            int_dict['state'] = data.get('state', '')
            # change 'eth_speed' to 'eth_bw' 31.07.2024
            #int_dict['speed'] = data.get('eth_speed', '')
            speed_val = int(data.get('eth_bw', 0))
            if speed_val >= 1000000:
                int_dict['speed'] = '{:4d} Gb/s'.format(speed_val // 1000000)
            elif speed_val >= 1000:
                int_dict['speed'] = '{:4d} Mb/s'.format(speed_val // 1000)
            else:
                int_dict['speed'] = ' - '
            
            # add interface errors
            int_dict['in_errors'] = int(data.get('eth_inerr'))
            int_dict['out_errors'] = int(data.get('eth_outerr'))

            # add interface result to interface dict
            self.interfaces[int_name] = int_dict.copy()

        self.exec_time = time.time() - self.timestamp
        self._first_run = False

#----------------------------
def short_if_name(if_name):
    short_name = if_name.replace('port-channel', 'Po').replace('Ethernet', 'Eth')
    return short_name

#----------------------------
def mainloop(stdscr, baseif_str, fexif_str, po_str, 
             start_interval, csv_file, error_counter):
# Mainloop function
    stat_list = []
    # start interval
    interval = start_interval
    stdscr.clear()
    # switch to nodelay for key input
    stdscr.nodelay(True)

    # print start 
    stdscr.addstr(
        'Collecting first interval, starting at: {}\n'
        .format(time.strftime('%H:%M:%S', time.localtime(time.time()))), 
        BOLD
    )
    stdscr.refresh()
    
    # first command execution to see if interface string is valid for the device
    if baseif_str != '':
        baseif = InterfaceStats(baseif_str)
        if not baseif.int_list_valid:
            stdscr.nodelay(False)
            return False, baseif_str
        stat_list.append(baseif)
    if fexif_str != '':
        fexif = InterfaceStats(fexif_str)
        if not fexif.int_list_valid:
            stdscr.nodelay(False)
            return False, fexif_str
        stat_list.append(fexif)
    if po_str != '':
        poif = InterfaceStats(po_str)
        if not poif.int_list_valid:
            stdscr.nodelay(False)
            return False, po_str
        stat_list.append(poif)
    
    # collect statistic data first time
    exec_time = 0.0
    for int_stat in stat_list:
        int_stat.get_stat()
        exec_time += int_stat.exec_time
    time.sleep(0.1)

    # main loop until program end by key press
    first_loop = True
    while True:
        loopstart = time.time()
        # activate busy flag on screen position 0,0
        stdscr.addstr(0, 0, 'BSY', WHITE_RED | BOLD)
        stdscr.refresh()
        
        # collect statistic data
        exec_time = 0.0
        for int_stat in stat_list:
            int_stat.get_stat()
            exec_time += int_stat.exec_time
        
        # clear busy flag on screen position 0,0
        stdscr.addstr(0, 0, '  ')
        stdscr.refresh()

        # prepare header line
        header_line = \
            '{:11} : {:15} : {:20}: {:10} : {:10} :'\
            .format('    Int', 'Speed and State', 'Description', 
                    FACTORSTR + ' in', FACTORSTR + ' out')
        if error_counter: # add error counter to header
            header_line += ' {:12} : {:12} :\n'.format('in-errors', 'out-errors')
        else:
            header_line += '\n'

        # print header line
        stdscr.addstr(0, 0, header_line, BOLD)

        # if logfile, write header to csv file
        if csv_file and first_loop:
            hrow = ['time']
            for int_stat in stat_list:
                for intf in int_stat.int_list:
                    hrow.append('{}-in'.format(short_if_name(intf)))
                    hrow.append('{}-out'.format(short_if_name(intf)))
            csv_file.writerow(hrow)
            first_loop = False

        if csv_file:
            row = []

        # loop through all interfaces lists
        for int_stat in stat_list:
            for intf in int_stat.int_list:
                # shorten interface output
                prnt_int_name = short_if_name(intf)
                # prepare output line
                output_line = '{:11} : {:10} {:4} : {:20}: {:10,.1f} : {:10,.1f} :'\
                    .format(
                        prnt_int_name[:11], 
                        int_stat.interfaces[intf]['speed'][:10],
                        int_stat.interfaces[intf]['state'][:4], 
                        int_stat.interfaces[intf]['description'][:20], 
                        int_stat.interfaces[intf]['in_tput'], 
                        int_stat.interfaces[intf]['out_tput']
                    )
                if error_counter: # add error counter to output line
                    output_line += ' {:12,.0f} : {:12,.0f} :\n'\
                    .format(
                        int_stat.interfaces[intf]['in_errors'],
                        int_stat.interfaces[intf]['out_errors']
                    )
                else:
                    output_line += '\n'
                # prepare attribute code - red if interface is down
                attribute_line = RED_WHITE | BOLD \
                    if int_stat.interfaces[intf]['state'] == 'down' else 0
                try:
                    stdscr.addstr(output_line, attribute_line)
                except curses.error:
                    stdscr.clear()
                    stdscr.addstr(
                        '...\n      --- increase screen size ---\n', 
                        WHITE_RED | BOLD
                    )
                # prepare logfile line if necessary
                if csv_file:
                    row.append(int_stat.interfaces[intf]['in_tput'])
                    row.append(int_stat.interfaces[intf]['out_tput'])
        
        #print footer line
        print_time = time.strftime('%H:%M:%S', time.localtime(loopstart))
        stdscr.addstr(
            'interval {:2.0f}s - Last Update: {} - Exec Time {:4.2f} - Press "Q" to end  '\
            .format(interval, print_time, exec_time)
            )
        stdscr.refresh()

        # write logfile line if necessary
        if csv_file:
            row.insert(0, print_time)
            csv_file.writerow(row)

        # --- end of loop - calculate wait time for next interation
        looptime = time.time() - loopstart
        # if execution takes longer than loop time, 
        # increase interval to addition start interval
        if looptime > interval:
            interval = interval + INTERVAL_ADD
        wait_time = interval - looptime
        # check key press
        while wait_time > 0.0:
            key_press = stdscr.getch()
            if key_press == 113 or key_press == 81:  # 'Q' or 'q'
                # switch to normal for key input
                stdscr.nodelay(False)
                return True, ''
            if key_press == 114 or key_press == 82: # 'R' or 'r'
                # redraw the entire screen
                stdscr.redrawwin()
                stdscr.refresh()

            time.sleep(min(0.2, wait_time))
            wait_time -= 0.2

#----------------
def main(stdscr, args):
    # --- screen preperation ----
    global BOLD
    BOLD = curses.A_BOLD
    global RED_WHITE
    global WHITE_RED
    global WHITE_BLUE
    # check if colors are possible (not on vt100 terminals)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        RED_WHITE = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        WHITE_RED = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        WHITE_BLUE = curses.color_pair(3)
    else:  # no color mode
        RED_WHITE = 0
        WHITE_RED = 0
        WHITE_BLUE = 0

    # activate break mode
    curses.cbreak()

    # --- parse input string with interfaces using precompiled REGEX strings ---
    # precompile the rexec strings
    baseif_re = re.compile('^(e|eth|ethernet)\d\/\d{1,2}(|\/\d{1,2})($|-\d{1,2})$', re.IGNORECASE)
    fexif_re = re.compile('^(e|eth|ethernet)\d{3}\/\d\/\d{1,2}($|-\d{1,2})$', re.IGNORECASE)
    po_re = re.compile('^(po|port-channel)\d{1,4}$', re.IGNORECASE)

    baseif_list, fexif_list, po_list = [], [], []
    baseif_str, fexif_str, po_str = '', '', ''
    unknown_if = []

    for element in args.if_list:
        for sub_element in element.split(','):
            # check for base interfaces
            if baseif_re.match(sub_element):
                baseif_list.append(sub_element)
            # check for fex ineterfaces
            elif fexif_re.match(sub_element):
                fexif_list.append(sub_element)
            # check for port-channels
            elif po_re.match(sub_element):
                po_list.append(sub_element)
            else:
                unknown_if.append(sub_element)

    # put lists into comma separated strings
    baseif_str = ','.join(baseif_list)
    fexif_str = ','.join(fexif_list)
    po_str = ','.join(po_list)
 
    # query input string
    if len(unknown_if) >0:
        stdscr.addstr('Unknown interface: {}\n\r'.format(",".join(unknown_if)))
        stdscr.addstr('press any key')
        stdscr.refresh()
        stdscr.getkey()
        exit()
    else:
        # open logfile if required
        if args.logfile:
            import sys
            import csv
            logfile = '/bootflash/{}'.format(args.logfile)
            try:
                f = open(logfile, 'w')
            except:
                sys.exit('Error open file {}'.format(logfile))
            csv_file = csv.writer(f, delimiter=',')
        else:
            csv_file = False
        # start mainloop
        valid, err = mainloop(
            stdscr, baseif_str, fexif_str, po_str, 
            float(args.interval), csv_file, args.error_counter
            )
        if args.logfile:
            f.close()
        if not valid:
            stdscr.clear()
            stdscr.addstr('Wrong interface {}\n\r'.format(err), BOLD)
            stdscr.addstr('press any key')
            stdscr.refresh()
            stdscr.getkey()
            exit()
    return

# start main
if __name__ == '__main__':
    # parse arguments

    parser = argparse.ArgumentParser(
        prog='Interface Performance Monitor',
        formatter_class=argparse.RawTextHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
        )
    parser.add_argument('if_list', type=str, nargs='+', metavar='Interface or Interface-list')
    parser.add_argument('-i','--interval', type=int, default=5, dest='interval', 
                        choices=range(5, 3600), metavar='5-3600')
    parser.add_argument('-e', '--error', dest='error_counter', action='store_true',
                        help='add error counter columns')
    parser.add_argument('-l', '--logfile', metavar='logfile', nargs='?',
                        const='intperf.csv', default=False, dest='logfile')
    args = parser.parse_args()

    try:
        #curses.use_env(False)
        wrapper(main, args)
    except KeyboardInterrupt:
        print('end')
