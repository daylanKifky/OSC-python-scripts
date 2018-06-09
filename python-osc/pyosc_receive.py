"""Simple OSC server

This program listens to one address, and prints some information about
received packets.
"""
import math
import time, threading
from sys import path as syspath
syspath.append("/usr/local/lib/python2.7/dist-packages")

from pythonosc import dispatcher
from pythonosc import osc_server


def print_recibed_msg(addr, args, *osc):
  """Print the recibed OSC message.

    Positional arguments:
    addr -- the OSC address that triggered the message
    args -- the dispatcher will pass the registered custom args (if any) as a tuple here.
    [note: if there ain't no registered custom args the dispatcher will pass the first osc message in this position]
    *osc -- the osc messages 
  """
  print("[{0}] - {1} {2}".format(addr, len(osc), args[0]))
  for i in range(len(osc)):
    print(osc[i])

#create the dispatcher
dispatcher = dispatcher.Dispatcher()
#register a handler to print on the address /print
dispatcher.map("/print", print_recibed_msg, "MSG")

#create and start the server
server = osc_server.OSCUDPServer(("localhost", 6565), dispatcher)
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