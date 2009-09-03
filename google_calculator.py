"""
    Google Calculator

    Designed for python 2.6

    Tested on Windows XP (so far) - should work on *nix systems

    Usage: "main.py COM5"

    Requires: 
        pyserial - http://pyserial.sourceforge.net/
        google api - http://github.com/thisismyrobot/Google-API/

    Licensing
    ---------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""

import serial
import sys
import time
import getpass
import google.api


calc_state = 0
port_name = sys.argv[1]

light_port = serial.Serial(port=port_name)
light_port.setRTS(0)
light_port.setDTR(0)

print "Enter 'C1+-' on the calculator before entering your username/password"

username = raw_input("Google Account Username: ")
password = getpass.getpass("Google Account Password: ")

while(1):

    connector = google.api.GoogleConnector(username, password)
    email_counter = connector.get_gmail_unread_count()
    reader_counter = connector.get_google_reader_unread_count()

    if reader_counter > 99:
        reader_counter = 99

    #work out difference, make into READER_COUNT.EMAIL_COUNT format
    calc_new_state = reader_counter + (email_counter * 100)  
    calc_diff = calc_new_state - calc_state 

    #update calculator by pressing the '+'/'-' keys
    if calc_diff > 0:
        for i in range(calc_diff):
            light_port.setRTS(1)
            time.sleep(0.01)
            light_port.setRTS(0)
            time.sleep(0.01)
    if calc_diff < 0:
        for i in range(-calc_diff):
            light_port.setDTR(1)
            time.sleep(0.01)
            light_port.setDTR(0)
            time.sleep(0.01)

    calc_state += calc_diff
    time.sleep(60)
