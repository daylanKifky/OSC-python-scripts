import bpy
import blf
from bpy.props import IntProperty, FloatProperty
from mathutils import *
from math import *

from os import system

import time, threading

from pythonosc import dispatcher
from pythonosc import osc_server

IP, PORT = "", 6565


system("clear")

D = bpy.data

class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"
    
    cube = D.objects['Cube']
    arm =  D.objects['Armature']
    bone = arm.pose.bones['Bone']

    bpy.types.Scene.quatBrazo = bpy.props.FloatVectorProperty(subtype='QUATERNION', name="brazoquat", size=4)
    quat = D.scenes['Scene'].quatBrazo

    transforming_rotation = D.objects['Armature'].data.bones['Bone'].matrix_local.to_quaternion()
 
    first_mouse_x = IntProperty()
    first_value = FloatProperty()

    diff = False
    lastQuat = Quaternion()

    views_3d =  [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D' ]  

    def modal(self, context, event):



        if event.type == 'TIMER':
            for a in self.views_3d:
                    a.header_text_set("Received {}".format(self.quat[0]))

            self.cube.rotation_quaternion  = self.quat

            if not self.diff:
                self.lastQuat = self.quat.slerp(self.lastQuat, 0.5)

            else:
                #this set the bone to the same rotation than the cube in world space
                q = self.transforming_rotation.conjugated() * self.cube.rotation_quaternion.copy() * self.transforming_rotation
                self.bone.rotation_quaternion = q * self.diff.conjugated()


        elif event.type == 'A':
            print("A")
            self.get_rot_diff(self.cube.rotation_quaternion)    

       #Finising     
        elif event.type == 'LEFTMOUSE':
            self.cancel(context)

            for a in self.views_3d:
                a.header_text_set()
            
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # context.object.location.x = self.first_value
            self.cancel(context)

            for a in self.views_3d:
                a.header_text_set()
            
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        """Start the timer"""
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.05, context.window)
        wm.modal_handler_add(self)

        #Start the server
        print("************INIT SERVER***************")
        self.startServer()

        """Place the cube near the bone"""
        l = self.bone.location.copy()
        l.rotate(self.transforming_rotation)
        self.cube.location = self.arm.location + l
        self.cube.location[0] -= 0.2
      
        return {'RUNNING_MODAL'}
        
    ###########################################
    ###     DEFINING CUSTOM METHODS         ###
    ###########################################

    def get_rot_diff(self, origin):
        q0 = self.transforming_rotation.conjugated() * origin.copy() * self.transforming_rotation
        self.diff = self.bone.rotation_quaternion.rotation_difference(q0)
        

    def cancel(self, context):
        """
        cancel() get's called when the operator is about to exit
        Here we remove the timer and stop the server
        """
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        print ("\nClosing OSCServer.")
        self.server.shutdown()
        print ("Waiting for Server-thread to finish")
        self.st.join() 
        print ("Done")



    def startServer(self):
        """
        Start the OSC server on different thread and attach a handler to the OSC address "/quats"
        """

        #create the dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        #register a handler to set the recived values on the address /quats
        #to a blender property somewhere
        self.dispatcher.map("/Chordata/.*", receive_Quat, self.quat)
        

        #Start evetything
        self.server = osc_server.OSCUDPServer((IP, PORT), self.dispatcher)
        self.st = threading.Thread( target = self.server.serve_forever)
        print("Serving on {}".format(self.server.server_address))
        self.st.start()

###########################################
###             OSC HANDLERS            ###
###########################################

def receive_Quat(addr, obj, *val):
    """
    OSC HANDLER get a tuple of 4 OSC values and set them the passed obj
    """
    print("RECEIVED ", val)
    if 4 == len(val):
        for i in range(4):
            obj[0][i] = float(val[i])




# bpy.utils.register_class(OscOperator)

def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
