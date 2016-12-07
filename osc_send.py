#!/usr/bin/python

import OSC

send_address = '127.0.0.1' , 7000

c = OSC.OSCClient()
c.connect(send_address)

msg = OSC.OSCMessage()
msg.setAddress("/quats")
msg.append("lalal")
msg.append(2500)
msg.append(3.14)
# msg.append(True)
c.send(msg)
