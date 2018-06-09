
# Point projection from:
# - https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix#answer-86570
# (@fnunnari's response)

import bpy
from mathutils import Vector


D=bpy.data
C=bpy.context

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client
from mathutils import Matrix
from time import sleep



IP='127.0.0.1'
PORT = 6767
client = udp_client.SimpleUDPClient(IP, PORT)

def send_Mesh(o: bpy.types.Object):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    msg = osc_message_builder.OscMessageBuilder(address="/vertex")
    
    me = o.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')

    
    for i,vert in enumerate(me.vertices):
        if len(msg.args)>998: break
        for co in vert.co:
            msg.add_arg(co)

    print(len(msg.args))
    bundle.add_content(msg.build())

    msg = osc_message_builder.OscMessageBuilder(address="/polys")


    for poly in me.polygons:
        for vert in poly.vertices:
            msg.add_arg(vert)

    bundle.add_content(msg.build())



    bundle = bundle.build()
    client.send(bundle)

def send_init_msg(o):
    client.send_message("/init", len(o.data.vertices))
    


def send_animation(o):
    timeline = C.scene.frame_start, C.scene.frame_end

    send_init_msg(o)

    delay = 1/C.scene.render.fps
    for i in range(*timeline):
        print("SEND FRAME", i)
        C.scene.frame_set(i)
        send_Mesh(o)    
        sleep(delay)    


class send_osc(bpy.types.Operator):
   
    """Receive quaternions from OSC and move an armature"""
    bl_idname = "object.send_osc"
    bl_label = "Send the animation trought OSC"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, ev): 
        print("SEND INVOKE")

        return self.execute(context)


    def execute(self, context):
        # deb =  note_debouncer()
        # piano_collide.unregister()
        send_animation(context.object)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(send_osc)
    # piano_collide.register()
    


def unregister():
    bpy.utils.unregister_class(send_osc)
    # piano_collide.unregister()



if __name__ == '__main__':
    register()    

    # send_animation(D.objects["TARGET"])
         




