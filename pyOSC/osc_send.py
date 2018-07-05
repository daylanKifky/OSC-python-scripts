#!/usr/bin/python

import OSC

send_address = '127.0.0.1' , 7777

c = OSC.OSCClient()
c.connect(send_address)

msg = OSC.OSCMessage()
msg.setAddress("/test")
msg.append("Test")
msg.append(2500)
msg.append(3.14)
# Sending Boolean not supported 
# msg.append(True)
c.send(msg)
