# This is an attempt to create randomly sampled points 

import sys
import pyglet
# Disable error checking for increased performance
#pyglet.options['debug_gl'] = False
import pyglet.graphics
import pyglet.gl

import time


from numfly.camera import Camera

pg = pyglet.gl

from pyglet.window import key
import numpy as n

cam = Camera()
cam.pos_speed = 0.5
window = cam.window

print(window.height)
print(window.width)

if len(sys.argv) > 1:
    filename = sys.argv[1]
    data = n.load(filename)
else:
    data = n.random.random([3,3,3])


npoints = min(data.size,10000000)

def convert(array):
    
    cum = n.cumsum(1.0*array.reshape(-1))
    cum /= cum[-1]
    # 1-D indices of randomly sampled points in accordance with array distribution
    indices = n.searchsorted(cum,n.random.random(npoints))
    i,j,k = n.unravel_index(indices,array.shape)

    i = i + n.random.random(npoints)
    j = j + n.random.random(npoints)
    k = k + n.random.random(npoints)

    x = n.array([i,j,k])
    return x.transpose().reshape(-1)

t0 = time.time()
print('Converting')
vertices = convert(data)

t1 = time.time()
print(f'Convert time {t1-t0} s')


vertex_list = pyglet.graphics.vertex_list(npoints,
                                          ('v3f',vertices))

vertex_list.draw(pyglet.gl.gl.GL_POINTS)


fps_display = pyglet.window.FPSDisplay(window=window)


@window.event
def on_draw():
    if not cam.draw():
        return False
    window.clear()
    vertex_list.draw(pyglet.gl.gl.GL_POINTS)
    fps_display.draw()

    
pyglet.clock.schedule_interval(cam.update, 1/60.0)

pyglet.app.run()
