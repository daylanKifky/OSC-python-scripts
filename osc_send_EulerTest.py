#!/usr/bin/python

import OSC, time

send_address = '127.0.0.1' , 7000

c = OSC.OSCClient()
c.connect(send_address)

msg = OSC.OSCMessage()
msg.setAddress("/quats")

for i in range(360):
	msg = OSC.OSCMessage()
	msg.setAddress("/quats")
	msg.append(i)
		
	print "sending ",i
	c.send(msg)
	time.sleep(0.3)
