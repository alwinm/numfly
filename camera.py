#import pyglet
# Disable error checking for increased performance
#pyglet.options['debug_gl'] = False
# import pyglet.graphics
import pyglet.gl
pg = pyglet.gl
import pyglet.window
key = pyglet.window.key

import numpy as n

def get_pressed_keys(key_dict):
    keys,values = key_dict.keys(),key_dict.values()
    keys = n.array(list(keys))
    values = n.array(list(values))
    if n.any(values):
        return keys[values]
    else:
        return []
    
class Camera:
    def __init__(self,rot_speed=1.0,pos_speed=10.0):
        self.window = pyglet.window.Window()
        self.window.projection = pyglet.window.Projection3D()
        self.cam_vector = n.array([0.,0.,-1.])
        self.cam_normal = n.array([0.,1.,0.])
        # 'up' means rotating cam_vector and cam_normal in direction of cam_normal
        # 'right' means rotating cam_vector and cam_normal perpendicular to cam_normal
        self.cam_pos = n.array([0.,0.,0.])
        self.rot_speed = rot_speed
        self.pos_speed = pos_speed
        # counter keeps track of update cycles
        self.counter = 0
        # pressed counter is the last time a key was pressed
        self.pressed_counter = 0

        self.key_state = {}
        @self.window.event
        def on_key_press(symbol,modifiers):
            self.key_state[symbol] = True
            return

        @self.window.event
        def on_key_release(symbol,modifiers):
            self.key_state[symbol] = False
            return

        
    def rot_vertical(self,speed):
        cos = n.cos(n.radians(speed))
        sin = n.sin(n.radians(speed))
        new_vector = cos*self.cam_vector + sin*self.cam_normal
        new_normal = cos*self.cam_normal - sin*self.cam_vector
        self.cam_vector = new_vector
        self.cam_normal = new_normal
        print(self.cam_vector)
        return new_vector,new_normal
    
    def rot_horizontal(self,speed):
        cos = n.cos(n.radians(speed))
        sin = n.sin(n.radians(speed))
        new_vector = sin*n.cross(self.cam_vector,self.cam_normal) + cos*self.cam_vector
        self.cam_vector = new_vector
        print(self.cam_vector)
        return new_vector

    def rot_around(self,speed):
        cos = n.cos(n.radians(speed))
        sin = n.sin(n.radians(speed))
        new_normal = sin * n.cross(self.cam_vector,self.cam_normal) + cos*self.cam_normal
        self.cam_normal = new_normal
        print(self.cam_vector)
        return new_normal

    def renorm(self):
        self.cam_vector = self.cam_vector/n.sqrt(n.sum(self.cam_vector**2.))
        self.cam_normal -= n.sum(self.cam_normal * self.cam_vector) * self.cam_vector
        self.cam_normal = self.cam_normal/n.sqrt(n.sum(self.cam_normal**2.))

    def update(self,dt):
        self.counter += 1
        pressed = get_pressed_keys(self.key_state)
        for item in pressed:
            if item == key.SPACE:
                self.cam_pos -= self.pos_speed*self.cam_vector
                print(self.cam_pos)
            elif item == key.LSHIFT:
                self.cam_pos += self.pos_speed*self.cam_vector
                print(self.cam_pos)
            elif item == key.ENTER:
                # reset
                self.cam_pos = n.zeros(3)
                self.cam_vector = n.array([0.,0.,-1.])
                self.cam_normal = n.array([0.,1.,0.])
            elif item == key.RSHIFT:
                print(self.cam_vector,self.cam_normal)
                self.renorm()
                print(self.cam_vector,self.cam_normal)
            elif item == key.A:
                self.rot_horizontal(-self.rot_speed)
            elif item == key.D:
                self.rot_horizontal(+self.rot_speed)
            elif item == key.W:
                self.rot_vertical(-self.rot_speed)
            elif item == key.S:
                self.rot_vertical(self.rot_speed)
            elif item == key.Q:
                self.rot_around(self.rot_speed)
            elif item == key.E:
                self.rot_around(-self.rot_speed)
                
            elif item == key.LEFT:
                self.rot_horizontal(-0.1*self.rot_speed)
            elif item == key.RIGHT:
                self.rot_horizontal(0.1*self.rot_speed)
            elif item == key.UP:
                self.rot_vertical(-0.1*self.rot_speed)
            elif item == key.DOWN:
                self.rot_vertical(0.1*self.rot_speed)
            elif item == key.I:
                self.cam_pos += self.pos_speed*self.cam_normal
            elif item == key.K:
                self.cam_pos -= self.pos_speed*self.cam_normal
            elif item == key.J:
                self.cam_pos -= self.pos_speed*n.cross(self.cam_normal,self.cam_vector)
            elif item == key.L:
                self.cam_pos += self.pos_speed*n.cross(self.cam_normal,self.cam_vector)
        if len(pressed):
            self.pressed_counter = self.counter
            return
    def draw(self):
        # do nothing if key was not pressed recently
        if self.counter > self.pressed_counter + 5:
            return False
        pg.glDisable(pg.GL_CULL_FACE)
        pg.glMatrixMode(pg.GL_PROJECTION)
        pg.glLoadIdentity()
        pg.gluPerspective(90, self.window.width/self.window.height, 1.0, 100000.0)
        pg.glMatrixMode(pg.GL_MODELVIEW)
        pg.glLoadIdentity()
        
        rot_matrix = n.zeros([4,4])
        rot_matrix[3,3] = 1.0
        rot_matrix[:3,:3] = n.array([n.cross(self.cam_normal,self.cam_vector),self.cam_normal,self.cam_vector])
        tran_matrix = n.diag(n.ones(4))
        tran_matrix[:3,3] = -self.cam_pos
        # ensures translation is done first, rotation second
        matrix = n.matmul(rot_matrix,tran_matrix)

        convert = (pg.GLfloat*16)(*matrix.transpose().reshape(-1))
        
        # then use desired normal vector and view vector to rotate view appropriately
        pg.glMultMatrixf(convert)
        return True


    
