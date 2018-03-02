import bpy
from mathutils import *
C = bpy.context
D= bpy.data


notes = [
	("NONE", "none", "", 0),
    ("C", "C", "", 1),
    ("C#", "C#", "", 2),
    ("D", "D", "", 3),
    ("D#", "D#", "", 5),
    ("E", "E", "", 5),
    ("F", "F", "", 6),
    ("F#", "F#", "", 7),
    ("G", "G", "", 8),
    ("G#", "D#", "", 9),
    ("A", "A", "", 10),
    ("A#", "A#", "", 11),
    ("B", "B", "", 12),
    ("NOT_SET", "not set", "", 13),
    ]


bpy.types.Object.note = bpy.props.EnumProperty(items=notes, default="NOT_SET")

bpy.types.Bone.player = bpy.props.BoolProperty(default=False)


def show_prop(self, context):
    if context.bone:
        self.layout.prop(context.bone, "player")


for ob in D.objects:
    if ob.note == "NOT_SET":
        ob.note = "NONE"



# def is_inside(p, obj, max_dist = 1.84467e+19):
#     # max_dist = 1.84467e+19
#     boh, point, normal, face = obj.closest_point_on_mesh(p, max_dist)
#     p2 = obj.matrix_world * point-p
#     v = p2.normalized().dot(normal)
#     # print(v)
#     return not(v < 0.0)


def is_inside(p, obj):
    radius = obj.data.vertices[0].co.copy()
    for i,x in enumerate(obj.scale):
        radius[i] *= x

    radius = radius.magnitude

    v =  p -obj.matrix_world.to_translation()
    return v.magnitude < radius

def register():
    bpy.types.BONE_PT_context_bone.prepend(show_prop)	

def unregister():
    bpy.types.BONE_PT_context_bone.remove(show_prop)   
