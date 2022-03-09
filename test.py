import sys
import pyglet
# Disable error checking for increased performance
#pyglet.options['debug_gl'] = False
import pyglet.graphics
import pyglet.gl

from numfly.camera import Camera

pg = pyglet.gl

from pyglet.window import key
import numpy as n

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


cam = Camera()
window = cam.window
#window = pyglet.window.Window()
#window.projection = pyglet.window.Projection3D()
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
rescale = min(window.width/data.shape[0],window.height/data.shape[1])
opoints[0::3] *= rescale
opoints[0::3] -= window.width/2
opoints[1::3] *= rescale
opoints[1::3] -= window.height/2
opoints[2::3] *= rescale

#opoints[2::3] -= window.width/2
npoints = int(len(opoints)/3)
print(opoints)
print('made points:',npoints,len(opoints))

vl2 = pyglet.graphics.vertex_list(npoints,
                                  ('v3f', opoints))
vl2.draw(pyglet.gl.gl.GL_POINTS)


fps_display = pyglet.window.FPSDisplay(window=window)


@window.event
def on_draw():
    if not cam.draw():
        return False
    window.clear()
    vl2.draw(pyglet.gl.gl.GL_POINTS)
    fps_display.draw()

    
pyglet.clock.schedule_interval(cam.update, 1/60.0)

pyglet.app.run()
