import bpy
from mathutils import Vector


D=bpy.data
C=bpy.context
cam = D.objects['the_cam']

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client
from mathutils import Matrix, Euler
from time import sleep
from math import pi
from os import system
from os import path
from sys import path as syspath


IP='127.0.0.1'
PORT = 6767
client = udp_client.SimpleUDPClient(IP, PORT)



def send_Armature(arm: bpy.types.Armature):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    
    for b in arm.pose.bones:
       
        #add coordinates
        msg = osc_message_builder.OscMessageBuilder(address="/chordata/"+b.name)
        q = b.matrix.to_quaternion()
        q.rotate(Euler((-pi/2,pi/2,0)))
        msg.add_arg( q[0])
        msg.add_arg( q[1])
        msg.add_arg( q[2])
        msg.add_arg( q[3])



        bundle.add_content(msg.build())
        
        #client.send_message("/point", (res[0], res[1]))
    
    # print("send frame: ", C.scene.frame_current )
    bundle = bundle.build()
    client.send(bundle)

def send_init_msg(arm):
    client.send_message("/init", len(arm.pose.bones))
    


def send_animation(arm):
    timeline = C.scene.frame_start, C.scene.frame_end

    send_init_msg(arm)

    delay = 1/C.scene.render.fps
    for i in range(*timeline):
        C.scene.frame_set(i)
        send_Armature(arm)    
        sleep(delay)    


class send_anim_osc(bpy.types.Operator):
   
    """Receive quaternions from OSC and move an armature"""
    bl_idname = "armature.send_anim_osc"
    bl_label = "Send the animation trought OSC"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, ev): 
        # print("SEND INVOKE")

        return self.execute(context)


    def execute(self, context):
        deb =  note_debouncer()
        piano_collide.unregister()
        send_animation(context.object)
        return {"FINISHED"}


class send_osc(bpy.types.Operator):
   
    """Receive quaternions from OSC and move an armature"""
    bl_idname = "armature.send_still_osc"
    bl_label = "Send the pose trought OSC"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, ev): 
        # print("SEND INVOKE")

        return self.execute(context)


    def execute(self, context):
        # deb =  note_debouncer()
        # piano_collide.unregister()
        send_Armature(context.object)
        return {"FINISHED"}


def register():
    print("SENDING OSC to {}:{}".format(IP, PORT))
    bpy.utils.register_class(send_osc)
    bpy.utils.register_class(send_anim_osc)
    
    


def unregister():
    bpy.utils.unregister_class(send_osc)
    bpy.utils.unregister_class(send_anim_osc)
    


if __name__ == '__main__':
    register()    

    # send_animation(D.objects["TARGET"])
         




