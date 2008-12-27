#'contents' is an array of elements, or None, to mean whatever the
#terrain generator specified

from __future__ import division
import pygame
from pygame.locals import *

import fff, gfx
from geom import *

class AlreadyDone(Exception):
  pass


def process_structural_failure():
  import random
  remaining = []
  for n in fff.broken_nodes:
    if random.randint(0,10) == 0:
      world.dig(n.x, n.y, n.z)
    else:
      remaining.append(n)

  fff.broken_nodes = remaining


    
class geo:
  def __init__(self):
    self.cubes = {}
    
  def __call__(self, x, y, z):
    if not self.cubes.has_key((x,y,z)):
      if z > 0:
        ret_val = None
      else:
        ret_val = virt_block(x,y,z)
      self.cubes[(x,y,z)] = ret_val
    return self.cubes[(x,y,z)]

  def at(self, c):
    (x,y,z) = c
    return self(x,y,z)

  def dig(self, x, y, z):
    c = self(x,y,z)
    if c != None:
      c.remove()
      self.cubes[(x,y,z)] = None
      for d in way.all:
        (dx, dy, dz) = (way.rel(d, (x,y,z)))
        print dx,dy,dz
        self.realize(dx, dy, dz)

  def construct(self, x, y, z):
    c = self(x,y,z)
    if c == None:
      self.cubes[(x,y,z)] = block(x,y,z)

  def invert(self, x, y, z):
    c = self(x,y,z)
    if c == None:
      self.construct(x,y,z)
    else:
      self.dig(x,y,z)

  def realize(self, x, y, z):
    c = self(x,y,z)
    if c == None: return
    if isinstance(c, virt_block):
      self.cubes[(x,y,z)].delete()
      self.cubes[(x,y,z)] = block(x, y, z)
  
world = geo()


class virt_block(gfx.sprite_3d, fff.sink):
  def __init__(self, x, y, z):
    gfx.sprite_3d.__init__(self, gfx.virt_block, x, y, z)
    fff.sink.__init__(self)
  
  def remove(self):
    self.delete()

class block(gfx.sprite_3d, fff.node):
  #initializing a block; the links must be set correct
  def __init__(self, x, y, z, realizing=False):
    gfx.sprite_3d.__init__(self, gfx.block, x, y, z)

    self.mass = 1
    fff.node.__init__(self,
                      [world.at(way.rel(d, (x,y,z)))
                       for d in way.all],
                      self.mass)

  def remove(self):
    self.fff(-self.mass) #remove our mass from the system
    self.cut_links()
    self.delete()
    
  def capacity_towards(self, d, safety_factor=1):
    if self.adj[d] == None:
      return 0
    elif d in way.horiz:
      return 6 / safety_factor - self.stress_on[d] #shear
    elif d == way.up:
      return 10 / safety_factor - self.stress_on[d] #tensile
    else: #d == way.down
      return 50 / safety_factor - self.stress_on[d] #compression

class rubble_pile(gfx.sprite_3d, fff.node):
  def __init__(self, x, y, z, mass):
    gfx.sprite_3d.__init__(self, gfx.block, x, y, z)

    self.mass = mass
    #only connected down
    fff.node.__init__(self,
                      [world.at(way.rel(d, (x,y,z)))
                       for d in way.all if d == way.down],
                      self.mass)
  def remove(self):
    self.fff(-self.mass)
    self.cut_links()
    self.delete()

  def capacity_towards(self, d, safety_factor=1):
    if self.adj[d] == None: return 0
    if d == way.down: return 10000
    else: return 0

    
