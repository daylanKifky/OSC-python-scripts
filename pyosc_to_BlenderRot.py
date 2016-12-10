""" 
Transform incoming osc messages to an object rotation

"""

import math
import time, threading

from pythonosc import dispatcher
from pythonosc import osc_server

from bpy import data as D

theObject = 'Cube'

# D.objects[theObject].rotation_mode = 'QUATERNION'
D.objects[theObject].rotation_mode = 'ZYX'

def osc_to_axis_Euler(addr, obj, val):
	D.objects[obj[0]].rotation_euler[2] = float(val)
	bpy.data.scenes[0].update()
	
	print(val)


def osc_to_quat(addr, objs, *quats):
  """Set the recibed quaternion as the obj rotation.

    Positional arguments:
    addr 	-- the OSC address that triggered the message
    objs 	-- [tuple] the name of the object(s) in which to set the rotation 
    *quat 	-- the quaternion as a tuple of four values 
  """
  for o in objs:
  	for i in range(len(quats)):
  		if i < 4:
  			D.objects[o].rotation_quaternion[i] = float(quats[i])
  			print(quats[i] ,end="\t")

  bpy.ops.object.visual_transform_apply()
  print("")

#create the dispatcher
dispatcher = dispatcher.Dispatcher()
#register a handler to print on the address /quats
dispatcher.map("/quats", osc_to_axis_Euler, theObject)

#create and start the server
server = osc_server.OSCUDPServer(("127.0.0.1", 7000), dispatcher)
st = threading.Thread( target = server.serve_forever)
print("Serving on {}".format(server.server_address))
st.start()

try :
    while 1 :
        time.sleep(5)

except KeyboardInterrupt :
    print ("\nClosing OSCServer.")
    server.shutdown()
    print ("Waiting for Server-thread to finish")
    st.join() ##!!!
    print ("Done")