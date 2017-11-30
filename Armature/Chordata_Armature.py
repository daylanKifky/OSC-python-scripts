import bpy
import threading
from pythonosc import dispatcher
from pythonosc import osc_server
import time, threading
from re import search as regex
from mathutils import *
from math import *


D = bpy.data
C = bpy.context

class Error(Exception):
	def __init__(self, msg):
		self.msg = msg

class Chordata:

	def __init__(self):
		self.object = None
		bpy.ops.object.mode_set(mode="OBJECT")
		self.message = " Chordata operator | Calibrating... Press AKEY to end "

		for o in D.objects:
			if o.type == "ARMATURE":
				self.object = o

		if self.object is None:
			raise Error("There's no Armature in the scene.")

		self.pose = self.object.pose.bones
		self.bones = self.object.data.bones
		self.temp = {}
		
		print("Bones found in armature")	
		for b in self.bones:
			b.use_inherit_rotation = False
			D.objects[b.name].rotation_mode = "QUATERNION"

			self.temp[b.name] = {}
			self.temp[b.name]["chord_quat"] = Quaternion()
			self.temp[b.name]["avg_quat"] = Quaternion()
			self.temp[b.name]["diff_quat"] = False
			self.temp[b.name]["local_q"] = b.matrix_local.to_quaternion()

			print(" [{}]".format(b.name))

		# print(self.object.pose.bones[0].rotation_quaternion)

		# self.object.pose.bones[0].rotation_quaternion = Quaternion() 	

		# print(self.object.pose.bones[0].rotation_quaternion)


	def put_quad_on_bones(self):
		# for b in self.bones:
		# 	self.pose[b.name].rotation_quaternion = b["chord_quat"]
			# print(self.pose[b.name].rotation_quaternion)
			
		for key, b in self.temp.items():
			D.objects[key].rotation_quaternion = b['chord_quat'] 
			
			if not b["diff_quat"]:
				b["avg_quat"] = b['chord_quat'].slerp(b["avg_quat"], 0.5)

			else:
				#this set the bone to the same rotation than the cube in world space
				q = b["local_q"].conjugated() * b['chord_quat'].copy() * b["local_q"]
				self.object.pose.bones[key].rotation_quaternion = q * b["diff_quat"].conjugated()

	def get_rot_diff(self):
		for key, b in self.temp.items():
		
			q0 = b["local_q"].conjugated() * b['avg_quat'].copy() * b["local_q"]
			b["diff_quat"] = self.object.pose.bones[key].rotation_quaternion.rotation_difference(q0)

		self.message = " Chordata operator | posing... "


	def start_server(self, IP = "", PORT = 6565):
		"""
		Start the OSC server on different thread and attach a handler to the OSC address "/quats"
		"""
		#create the dispatcher
		self.dispatcher = dispatcher.Dispatcher()
		#register a handler to get the recived values on the address /Chordata
		self.dispatcher.map("/Chordata/.*", receive, self)
	
		#Start evetything
		self.server = osc_server.BlockingOSCUDPServer((IP, PORT), self.dispatcher)
		self.st = threading.Thread( target = self.server.serve_forever,)
		print("Serving on {}".format(self.server.server_address))
		self.st.start()

	def close_server(self):
		print ("\nClosing OSCServer.")
		self.server.shutdown()
		print ("Waiting for Server-thread to finish")
		self.st.join() 
		print ("Done")


def receive(addr, objs, *osc_vals):
	sensor = regex("^/Chordata/(\w.*)", addr)
	if not sensor or sensor.lastindex < 1:
		print("Invalid address")
		return
	# print(osc_vals)

	try:
		for x in range(len(osc_vals)):
			objs[0].temp[sensor.group(1)]["chord_quat"][x] = float(osc_vals[x])
	
	except IndexError as e:
		print("An OSC lecture came with too much values")
		return

	except Exception as e:
		print("There was an error while reading 0SC data")
		print(e)
		return




# if __name__ == '__main__':
	# c =  Chordata()

	# try:
	# 	c.start_server()
		
	# except KeyboardInterrupt as e:
	# 	del c