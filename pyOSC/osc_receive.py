#!/usr/bin/python

import OSC
import time, threading



# tupple with ip, port.
receive_address = '' , 7777

# OSC Server. 
s = OSC.OSCServer(receive_address) 

# this registers a 'default' handler (for unmatched messages), 
# an /'error' handler, an '/info' handler.
# And, if the client supports it, a '/subscribe' & '/unsubscribe' handler
s.addDefaultHandlers()

def stamp_all(addr, tags, stuff, source):
	print addr #/print
	print tags #sif
	print stuff #['Test', 2500, 3.140000104904175]
	print source #('127.0.0.1', 40232)

def samplerate(addr, tags, stuff, source):
    print ""

s.addMsgHandler("/test", stamp_all) # adding our function


# just checking which handlers we have added
print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
    print addr

# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = s.serve_forever )
st.start()

try :
    while 1 :
        time.sleep(5)

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    s.close()
    print "Waiting for Server-thread to finish"
    st.join() ##!!!
    print "Done"
