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

cam = Camera()
cam.pos_speed = 0.5
window = cam.window

pg.glEnable(pg.GL_DEPTH_TEST)

#window = pyglet.window.Window()
#window.projection = pyglet.window.Projection3D()
print(window.height)
print(window.width)

data = n.random.random([3,3,3])

# This is a failed attempt to make transparency


def convert(array):
    shape = array.shape
    i,j,k = n.unravel_index(range(array.size),array.shape)

    x = n.array([i,j,k,
                 i+1,j,k,
                 i+1,j+1,k,
                 i,j+1,k,
                 i,j,k,
                 i+1,j,k,
                 i+1,j,k+1,
                 i,j,k+1,
                 i,j,k,
                 i,j+1,k,
                 i,j+1,k+1,
                 i,j,k+1,
    ])

    return x.transpose().reshape(-1)

def make_color(array):
    ones = n.ones(array.shape)
    
    x = n.array(3*4*[array,
                   array,
                   array,
                 0.1*array])
    return x.transpose().reshape(-1)

vertices = convert(data)
colors = make_color(data)

npoints = data.size*12
# 3 square for each datum
# 4 corners each square

vertex_list = pyglet.graphics.vertex_list(npoints,
                                          ('v3f',vertices),
                                          ('c4f',colors))

vertex_list.draw(pyglet.gl.gl.GL_QUADS)


fps_display = pyglet.window.FPSDisplay(window=window)


@window.event
def on_draw():
    if not cam.draw():
        return False
    window.clear()
    vertex_list.draw(pyglet.gl.gl.GL_QUADS)
    fps_display.draw()

    
pyglet.clock.schedule_interval(cam.update, 1/60.0)

pyglet.app.run()
