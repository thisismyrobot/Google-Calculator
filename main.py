"""
    Google Calculator
    
    Designed for python 2.6
    
    Tested on Windows XP (so far)
    
    Usage: main.py COM5
    
    Requires: pyserial
"""
import serial
import sys
import urllib
import urllib2
import base64
import time
import xml.dom.minidom

calc_state = 0
port_name = sys.argv[1]

light_port = serial.Serial(port=port_name)
light_port.setRTS(0)
light_port.setDTR(0)

print "Enter 'C1+-' on the calculator before entering your username/password"

while(1):

    #get gmail data. this triggers a username/pass prompt
    email_connection = urllib.urlopen('https://gmail.google.com/gmail/feed/atom')
    email_data = email_connection.read();
    email_connection.close()
    email_dom = xml.dom.minidom.parseString(email_data)
    email_counter = int(email_dom.getElementsByTagName('fullcount')[0].childNodes[0].data)

    #tricky bit; the next call needs username and password, so we grab them from the previous call
    #the rsplit is to cover the possibility of a "@" or ":" in the username/password
    #this is a mess and getPass() etc should be used.
    username = email_connection.url.split('https://')[1].rsplit(':')[0]
    password = email_connection.url.split('https://')[1].rsplit(':')[1].rsplit('@')[0]

    #get reader data (pain in the bum google reader api)
    reader_auth = urllib.urlencode(dict(Email=username, Passwd=password))
    reader_sid = urllib2.urlopen('https://www.google.com/accounts/ClientLogin', reader_auth).read().split("\n")[0]
    reader_request = urllib2.Request('http://www.google.com/reader/api/0/unread-count?all=true')
    reader_request.add_header('Cookie', reader_sid)
    reader_connection = urllib2.urlopen(reader_request)
    reader_data = reader_connection.read()
    reader_connection.close()
    reader_dom = xml.dom.minidom.parseString(reader_data)
    reader_counter = 0
    for reader_dom_object in reader_dom.getElementsByTagName('object'):
        if reader_dom_object.getElementsByTagName('string'):
            if str(reader_dom_object.getElementsByTagName('string')[0].childNodes[0].data).endswith('google/reading-list'):
                reader_counter = int(reader_dom_object.getElementsByTagName('number')[0].childNodes[0].data)
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
