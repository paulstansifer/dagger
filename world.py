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
      for d in way.all:
        (dx, dy, dz) = (way.rel(d, (x,y,z)))
        self.realize(dx, dy, dz)

      self.cubes[(x,y,z)] = None
      c.remove()



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
      self.cubes[(x,y,z)].remove()
      self.cubes[(x,y,z)] = block(x, y, z)
  
world = geo()


class virt_block(gfx.sprite_3d, fff.sink):
  def __init__(self, x, y, z):
    gfx.sprite_3d.__init__(self, gfx.virt_block, x, y, z)
  
  def remove(self):
    self.cut_links()
    self.delete()

  #these silently swallow writes because they are kept consistent by
  #the other side of the link, a non-virtual node (virtual<->virtual
  #interactions are trivial

  def _get_adj(self):
    return [world.at(way.rel(d, (self.x, self.y, self.z)))
                     for d in way.all]
  adj = property(_get_adj)

  def _get_stress_on(self):
    def negative_stress_on_if_applicable(node, d):
      if isinstance(node,block):
        return -node.stress_on[d]
      return 0 #if it's not a block, it can't transmit stress

    return [negative_stress_on_if_applicable(self.adj[d],way.opposite(d))
            for d in way.all]

  stress_on = property(_get_stress_on)

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

  

class rubble_pile(block):
  pass #TODO.  Only can be connected downwards
    
