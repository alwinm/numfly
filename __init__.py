import sys
import ctypes
import pyglet
# Disable error checking for increased performance
#pyglet.options['debug_gl'] = False
import pyglet.graphics
import pyglet.gl
pg = pyglet.gl

from pyglet.window import key
import numpy as n
pyglet.counter = 0
pyglet.pressed_counter = 0

def find_edges(mask):
    edges = n.zeros(mask.shape)
    pw = n.zeros([mask.ndim,2],dtype=int)
    slices = [slice(1,None),slice(None,-1)]
    for axis in range(mask.ndim):
        diff = n.abs(n.diff(mask,axis=axis))
        for i in range(2):
            sel = [slice(None)]*mask.ndim
            sel[axis] = slices[i]
            edges[tuple(sel)] += diff
    return edges > 0.0

def binner(array):
    for axis in range(array.ndim):
        asa = array.shape[axis]
        masa = asa - asa%2
        s1 = slice(1,masa,2)
        s2 = slice(0,masa,2)
        sel1 = array.ndim*[slice(None)]
        sel2 = array.ndim*[slice(None)]
        sel1[axis] = s1
        sel2[axis] = s2
        array = array[tuple(sel1)] + array[tuple(sel2)]
    return array > 0.0

def edges_to_points(edges):
    # XYZ coords in v3f openGL order
    return n.array(n.where(edges)).transpose().reshape(-1).astype(float)

    
    
def make_dirdict():
    dirdict = {}
    dirdict[key.A] = [-1,0]
    dirdict[key.D] = [1,0]
    dirdict[key.S] = [0,-1]
    dirdict[key.W] = [0,1]
    dirdict[key.LEFT] = [-1,0]
    dirdict[key.RIGHT] = [1,0]
    dirdict[key.DOWN] = [0,-1]
    dirdict[key.UP] = [0,1]
    return dirdict

window = pyglet.window.Window()
window.projection = pyglet.window.Projection3D()
print(window.height)
print(window.width)


filename = sys.argv[1]
data = n.load(filename)
while n.sum(data) > 1e7:
    data = binner(data)
opoints = 1.0*edges_to_points(data)
#edges = find_edges(binner(binner(binner(n.load(filename)))))
#opoints = 1.0*edges_to_points(edges)
# rescale and center on 0
opoints[0::3] *= window.width/data.shape[0]
opoints[0::3] -= window.width/2
opoints[1::3] *= window.height/data.shape[1]
opoints[1::3] -= window.height/2
#opoints[2::3] *= -1

#opoints[2::3] -= window.width/2
npoints = int(len(opoints)/3)
print(opoints)
print('made points:',npoints,len(opoints))

vl2 = pyglet.graphics.vertex_list(npoints,
                                  ('v3f', opoints))
vl2.draw(pyglet.gl.gl.GL_POINTS)


fps_display = pyglet.window.FPSDisplay(window=window)

cam_rot = [0,0]
cam_vector = n.array([0.,0.,-1.])
cam_normal = n.array([0.,1.,0.])
# 'up' means rotating cam_vector and cam_normal in direction of cam_normal
# 'right' means rotating cam_vector and cam_normal perpendicular to cam_normal
rot_speed = 1.
cam_pos = n.array([0.,0.,0.])
pos_speed = 10.

key_state = {}


def rot_vertical(speed):
    global cam_vector
    global cam_normal
    cos = n.cos(n.radians(speed))
    sin = n.sin(n.radians(speed))
    new_vector = cos*cam_vector + sin*cam_normal
    new_normal = cos*cam_normal - sin*cam_vector
    cam_vector = new_vector
    cam_normal = new_normal
    print(cam_vector)
    return new_vector,new_normal
    
def rot_horizontal(speed):
    global cam_vector
    cos = n.cos(n.radians(speed))
    sin = n.sin(n.radians(speed))
    new_vector = sin*n.cross(cam_vector,cam_normal) + cos*cam_vector
    cam_vector = new_vector
    print(cam_vector)
    return new_vector

def rot_around(speed):
    global cam_normal
    cos = n.cos(n.radians(speed))
    sin = n.sin(n.radians(speed))
    new_normal = sin * n.cross(cam_vector,cam_normal) + cos*cam_normal
    cam_normal = new_normal
    print(cam_vector)
    return new_normal

def renorm():
    global cam_vector
    global cam_normal
    cam_vector = cam_vector/n.sqrt(n.sum(cam_vector**2.))
    cam_normal -= n.sum(cam_normal * cam_vector) * cam_vector
    cam_normal = cam_normal/n.sqrt(n.sum(cam_normal**2.))

def get_pressed_keys(key_dict):
    keys,values = key_dict.keys(),key_dict.values()
    keys = n.array(list(keys))
    values = n.array(list(values))
    if n.any(values):
        return keys[values]
    else:
        return []
    
camdict = make_dirdict()
def update(dt):
    global cam_pos
    global cam_rot
    global cam_vector
    global cam_normal
    pyglet.counter += 1
    pressed = get_pressed_keys(key_state)
    for item in pressed:
        if item == key.SPACE:
            cam_pos -= pos_speed*cam_vector
            print(cam_pos)
        elif item == key.LSHIFT:
            cam_pos += pos_speed*cam_vector
            print(cam_pos)
        elif item == key.ENTER:
            # reset
            cam_pos = n.zeros(3)
            cam_vector = n.array([0.,0.,-1.])
            cam_normal = n.array([0.,1.,0.])
        elif item == key.RSHIFT:
            print(cam_vector,cam_normal)
            renorm()
            print(cam_vector,cam_normal)
        elif item == key.A:
            rot_horizontal(-rot_speed)
        elif item == key.D:
            rot_horizontal(+rot_speed)
        elif item == key.W:
            rot_vertical(-rot_speed)
        elif item == key.S:
            rot_vertical(rot_speed)
        elif item == key.Q:
            rot_around(rot_speed)
        elif item == key.E:
            rot_around(-rot_speed)
            
        elif item == key.LEFT:
            rot_horizontal(0.1*rot_speed)
        elif item == key.RIGHT:
            rot_horizontal(-0.1*rot_speed)
        elif item == key.UP:
            rot_vertical(-0.1*rot_speed)
        elif item == key.DOWN:
            rot_vertical(0.1*rot_speed)
        elif item == key.I:
            cam_pos += pos_speed*cam_normal
        elif item == key.K:
            cam_pos -= pos_speed*cam_normal
        elif item == key.J:
            cam_pos -= pos_speed*n.cross(cam_normal,cam_vector)
        elif item == key.L:
            cam_pos += pos_speed*n.cross(cam_normal,cam_vector)
    if len(pressed):
        pyglet.pressed_counter = pyglet.counter
    return

@window.event
def on_key_press(symbol,modifiers):
    key_state[symbol] = True
    return

@window.event
def on_key_release(symbol,modifiers):
    key_state[symbol] = False
    return

@window.event
def on_draw():
    if pyglet.counter - pyglet.pressed_counter > 5:
        return
    #pg.glDisable(pg.GL_DEPTH_TEST)
    pg.glDisable(pg.GL_CULL_FACE)
    #pg.glViewport(0,0,window.width,window.height)
    pg.glMatrixMode(pg.GL_PROJECTION)
    pg.glLoadIdentity()
    pg.gluPerspective(90, window.width/window.height, 1.0, 100000.0)
    #pg.glOrtho(0, window.width, 0, window.height, -1, 1)

    pg.glMatrixMode(pg.GL_MODELVIEW)
    pg.glLoadIdentity()
    # first move camera to desired location
    

    rot_matrix = n.zeros([4,4])
    rot_matrix[3,3] = 1.0
    rot_matrix[:3,:3] = n.array([n.cross(cam_normal,cam_vector),cam_normal,cam_vector])
    tran_matrix = n.diag(n.ones(4))
    tran_matrix[:3,3] = -cam_pos
    matrix = n.matmul(rot_matrix,tran_matrix)
    # ensures translation is done first, rotation second
    #matrix[:3,3] = cam_pos
    convert = (pg.GLfloat*16)(*matrix.transpose().reshape(-1))

    # then use desired normal vector and view vector to rotate view appropriately

    pg.glMultMatrixf(convert)
    #pg.glTranslatef(-cam_pos[0],-cam_pos[1],-cam_pos[2])

    '''
    dist = 1000.0
    #pg.gluLookAt(0,0,0,0,0,1000,0,1,0)
    pg.gluLookAt(cam_pos[0],cam_pos[1],cam_pos[2],
                 cam_pos[0]+dist*cam_vector[0],
                 cam_pos[1]+dist*cam_vector[1],
                 cam_pos[2]+dist*cam_vector[2],
                 cam_normal[0],
                 cam_normal[1],
                 cam_normal[2],
    )
    '''
    window.clear()
    vl2.draw(pyglet.gl.gl.GL_POINTS)
    fps_display.draw()




pyglet.clock.schedule_interval(update, 1/60.0)

pyglet.app.run()
