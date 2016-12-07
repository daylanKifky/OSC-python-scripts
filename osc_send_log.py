#!/usr/bin/python

import OSC, time

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

with open('../Quaternion_05-12-16.log') as f:
    lines = f.readlines()

for line in lines:
	quat = line.rstrip('\t\n').split('\t')
	msg = OSC.OSCMessage()
	msg.setAddress("/quats")
	# msg.append("un quat")
	for q in quat:
		msg.append(q)
		
	print "sending ",quat
	c.send(msg)
	time.sleep(0.1)
