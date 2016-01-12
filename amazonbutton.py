# if you want to run this script as an ubuntu service, check out
# http://askubuntu.com/questions/175751/how-do-i-run-a-python-script-in-the-background-and-restart-it-after-a-crash

import socket
import struct
import binascii
import time
import json
import urllib2

# Enter your IFTTT key between the quoted below:
ifttt_key = ''

# Each button has a MAC address.  Name them here.  These names will be used as the event name
# when triggering the IFTTT maker channel, e.g. https://maker.ifttt.com/trigger/<nickname>/with/key/<ifttt_key>
buttons = {
    'f0272d3e5ba4' : 'gillette_doorbell',
    '74c246395926' : 'meyers',
    '747548e6b034' : 'icebreakers',
}

# Trigger a IFTTT URL where the event is the same as the strings in macs (e.g. dash_gerber)
# Body includes JSON with timestamp values.
def trigger_url_generic(trigger):
    data = '{ "value1" : "' + time.strftime("%Y-%m-%d") + '", "value2" : "' + time.strftime("%H:%M") + '" }'
    req = urllib2.Request( 'https://maker.ifttt.com/trigger/'+trigger+'/with/key/'+ifttt_key , data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()
    return response

def record_trigger(trigger):
    print 'triggering '+ trigger +' event, response: ' + trigger_url_generic(trigger)

rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))

while True:
    packet = rawSocket.recvfrom(2048)
    ethernet_header = packet[0][0:14]
    ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
    # skip non-ARP packets
    ethertype = ethernet_detailed[2]
    if ethertype != '\x08\x06':
        continue
    arp_header = packet[0][14:42]
    arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
    source_mac = binascii.hexlify(arp_detailed[5])
    source_ip = socket.inet_ntoa(arp_detailed[6])
    dest_ip = socket.inet_ntoa(arp_detailed[8])
    
    button_clicked = False    
    # cull out unwanted signals coming from Amazon buttons
    if source_mac != "3060237e5a80" and source_mac != "6c29955ac8c3":
      for button in buttons:
        if source_mac == button:
          record_trigger(buttons[source_mac])
          button_clicked = True
    if (button_clicked != True) and (source_ip == '0.0.0.0'):
      print "Unknown MAC detected: " + source_mac