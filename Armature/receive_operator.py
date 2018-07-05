import bpy

from bpy.props import IntProperty, FloatProperty
from mathutils import *
from math import *

# import pdb

from os import system
from os import path
from sys import path as syspath

# from pythonosc import dispatcher
# from pythonosc import osc_server

syspath.append(path.dirname(bpy.data.filepath))

import Chordata_Armature as chordata
import send_arm_osc as send
from importlib import reload
reload(chordata)
reload(send)

system("clear")

D = bpy.data
C = bpy.context

do_send_osc = True 

def check_sc_fr_end(context):
    sc = context.scene
    if sc.frame_current > sc.frame_end:
        sc.frame_current = sc.frame_start

class Send_Anim_Osc(bpy.types.Operator):
   
    """Send Chordata armature animation trough OSC"""
    bl_idname = "object.send_anim_osc"
    bl_label = "Send Chordata Animation OSC"

    def invoke(self, context, event):
        return self.execute(context);

    def execute(self, context):
        for o in D.objects:
            if o.type == "ARMATURE":
                self.object = o

        if self.object is None:
            raise Error("There's no Armature in the scene.")

        sc = context.scene
        if sc.frame_current < sc.frame_start:
            sc.frame_current = sc.frame_start

        check_sc_fr_end(context)

        wm = context.window_manager
        self._timer = wm.event_timer_add( 1 / context.scene.render.fps , context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            send.send_Armature(self.object)
            context.scene.frame_current += 1
            check_sc_fr_end(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("ESQUING")

            self.cancel(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)



class ReceiveOperator(bpy.types.Operator):
   
    """Receive quaternions from OSC and move an armature"""
    bl_idname = "object.receive_operator"
    bl_label = "Receive Chordata Armature"
   
    views_3d =  [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D' ]  

    def __init__(self):
        self.chord = chordata.Chordata()
        self.last_event = ""

    def invoke(self, context, event):
        """Start the timer"""

        if context.scene.layers[10]:
            do_send_osc = True
            print ("^"*10, "SENDING OSC TO:", send.IP, send.PORT)
        else:
            do_send_osc = False
            print("^"*10, "NOT SENDING OSC!")
        
        wm = context.window_manager
        self._timer = wm.event_timer_add( 1 / context.scene.render.fps , context.window)
        wm.modal_handler_add(self)

        self.chord.start_server()
        
        self.text(self.chord.message)


        D.scenes['Scene'].layers[0] = True
        D.scenes['Scene'].layers[1] = True
        D.scenes['Scene'].layers[2] = True

        if do_send_osc:
            send.send_init_msg(self.chord.object)

        self.do_set_keyframes = False
        context.scene.frame_current = 0
        context.scene.frame_start = 0

        self.chord.reset_pose()

        return {'RUNNING_MODAL'}

    def text(self, text):
        for a in self.views_3d:
                a.header_text_set(text)


    def modal(self, context, event):
        if context.scene.layers[10]:
            do_send_osc = True
        else:
            do_send_osc = False

        if event.type == 'TIMER':
            self.chord.put_quad_on_bones()

            if do_send_osc:
                send.send_Armature(self.chord.object)

            if self.do_set_keyframes:
                self.chord.set_key(context)
                context.scene.frame_current += 1

        elif event.type == 'A':
            self.chord.get_rot_diff()
            self.text(self.chord.message)

        elif event.type == "Q":
            D.scenes['Scene'].layers[0] = False

        elif event.type == "K":
            self.chord.object.animation_data_clear()
            self.do_set_keyframes = True
            self.report({"INFO"}, "Registering animation!")

        elif event.type == "W":
            D.scenes['Scene'].layers[1] = False

        elif event.type == "E":
            D.scenes['Scene'].layers[2] = False

        elif event.type == "R":
            D.scenes['Scene'].layers[0] = True
            D.scenes['Scene'].layers[1] = True
            D.scenes['Scene'].layers[2] = True


        # elif event.type == 'LEFTMOUSE':
        #     self.cancel(context)
        #     return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            print("ESQUING")

            if self.chord.object.animation_data:
                context.scene.frame_end = self.chord.object.animation_data.action.frame_range[1]

            wm = context.window_manager
            wm.event_timer_remove(self._timer)

            self.chord.server.shutdown()
            self.chord.server.socket.close()
            self.chord.st.join()

            for a in self.views_3d:
                a.header_text_set()

            # pdb.set_trace()
            # self.cancel(context)
            return {'CANCELLED'}

        self.last_event = event.type

        return {'RUNNING_MODAL'}

        

    def cancel(self, context):
        """
        cancel() get's called when the operator is about to exit
        Here we remove the timer and stop the server
        """
        print("CANCELLING")

        wm = context.window_manager
        wm.event_timer_remove(self._timer)

        self.text("Closing server..")
        # self.chord.close_server()
        
        self.chord.server.shutdown()
        self.chord.st.join()
        
        for a in self.views_3d:
            a.header_text_set()

    # ###########################################
    # ###     DEFINING CUSTOM METHODS         ###
    # ###########################################

        
        

def register():
    # send.register()
    bpy.utils.register_class(ReceiveOperator)
    bpy.utils.register_class(Send_Anim_Osc)


def unregister():
    bpy.utils.unregister_class(ReceiveOperator)
    bpy.utils.unregister_class(Send_Anim_Osc)
    # send.unregister()


if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.object.receive_operator('INVOKE_DEFAULT')
