
# Point projection from:
# - https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix#answer-86570
# (@fnunnari's response)

import bpy
from mathutils import Vector

def project_3d_point(camera: bpy.types.Object,
                     p: Vector,
                     render: bpy.types.RenderSettings = bpy.context.scene.render) -> Vector:
    """
    Given a camera and its projection matrix M;
    given p, a 3d point to project:

    Compute P’ = M * P
    P’= (x’, y’, z’, w')

    Ignore z'
    Normalize in:
    x’’ = x’ / w’
    y’’ = y’ / w’

    x’’ is the screen coordinate in normalised range -1 (left) +1 (right)
    y’’ is the screen coordinate in  normalised range -1 (bottom) +1 (top)

    :param camera: The camera for which we want the projection
    :param p: The 3D point to project
    :param render: The render settings associated to the scene.
    :return: The 2D projected point in normalized range [-1, 1] (left to right, bottom to top)
    """

    if camera.type != 'CAMERA':
        raise Exception("Object {} is not a camera.".format(camera.name))

    if len(p) != 3:
        raise Exception("Vector {} is not three-dimensional".format(p))

    # Get the two components to calculate M
    modelview_matrix = camera.matrix_world.inverted()
    projection_matrix = camera.calc_matrix_camera(
        render.resolution_x,
        render.resolution_y,
        render.pixel_aspect_x,
        render.pixel_aspect_y,
    )

    # print(projection_matrix * modelview_matrix)

    # Compute P’ = M * P
    p1 = projection_matrix * modelview_matrix * Vector((p.x, p.y, p.z, 1))

    # Normalize in: x’’ = x’ / w’, y’’ = y’ / w’
    p2 = Vector(((p1.x/p1.w, p1.y/p1.w)))

    return p2





D=bpy.data
C=bpy.context
cam = D.objects['the_cam']

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client
from mathutils import Matrix
from time import sleep

from os import system
from os import path
from sys import path as syspath

syspath.append(path.dirname(bpy.data.filepath))
import piano_collide
import imp
imp.reload(piano_collide)

# piano_collide.unregister()


IP='127.0.0.1'
PORT = 6767
client = udp_client.SimpleUDPClient(IP, PORT)


class note_debouncer:
    zero_v = Vector()
    def __init__(self):
        self.last_frame = {}

    def calculate(self, point, ob):
        inside = piano_collide.is_inside(point, ob)
        # print(inside)
        pressing = False
        vel = self.zero_v

        if ob.name in self.last_frame.keys():
            pressing = self.is_pressing(ob.name, inside)
            vel = self.velocity(ob.name, point)

        self.last_frame[ob.name] = (inside, point)
        return pressing, vel        

    def is_pressing(self, name, state):
        # result = False
        # if name in self.last_frame.keys():
        # print("#"*20,state, self.last_frame[name][0])
        #     result = (state ^ self.last_frame[name]) & state

        # self.last_frame[name] = (state,)
        return (state ^ self.last_frame[name][0]) & state

    def velocity(self, name, pos):
        return  (pos - self.last_frame[name][1]).magnitude





deb =  note_debouncer()

def send_Armature(arm: bpy.types.Armature):
    bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
    msg = osc_message_builder.OscMessageBuilder(address="/point")
    
    res = project_3d_point(cam, arm.location)
    msg.add_arg(res[0])
    msg.add_arg(res[1])
    
    #client.send_message("/point", (res[0], res[1]))
    
    for b in arm.pose.bones:
        M = arm.matrix_world * b.matrix * Matrix.Translation((0,b.vector.magnitude,0))
        w_loc = M.to_translation()
        res = project_3d_point(cam, w_loc)



        if arm.data.bones[b.name].player:
            # bpy.ops.object.empty_add(radius = 0.1, location= w_loc)
            for ob in D.objects:
                if ob.note not in ["NONE", "NOT_SET"]:
                    # print(ob,w_loc, ob.note)
                    press, vel = deb.calculate(w_loc, ob)
                    if press:
                    
                        print("NOTE", ob.note, vel)
                        msg = osc_message_builder.OscMessageBuilder(address="/note")
                        msg.add_arg(ob.note)
                        msg.add_arg(vel)
                        bundle.add_content(msg.build())

        
        #add coordinates
        msg = osc_message_builder.OscMessageBuilder(address="/point")
        msg.add_arg(res[0])
        msg.add_arg(res[1])
        bundle.add_content(msg.build())
        
        #client.send_message("/point", (res[0], res[1]))
        # print("#"*10, b.name)
    
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


class send_osc(bpy.types.Operator):
   
    """Receive quaternions from OSC and move an armature"""
    bl_idname = "armature.send_osc"
    bl_label = "Send the animation trought OSC"

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, ev): 
        print("SEND INVOKE")

        return self.execute(context)


    def execute(self, context):
        deb =  note_debouncer()
        piano_collide.unregister()
        send_animation(context.object)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(send_osc)
    piano_collide.register()
    


def unregister():
    bpy.utils.unregister_class(send_osc)
    piano_collide.unregister()



if __name__ == '__main__':
    register()    

    # send_animation(D.objects["TARGET"])
         




