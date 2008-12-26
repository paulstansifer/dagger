#! /usr/local/bin/python
import pygame
from pygame.locals import *

import world, gfx

def fade(img, depth):
  ret_val = img.copy()
  if(depth == 0): return ret_val

  for x in xrange(ret_val.get_width()):
    for y in xrange(ret_val.get_height()):
      (r, g, b, a) = ret_val.get_at((x,y))
      ret_val.set_at((x,y), (128*depth + r*(1-depth),
                         128*depth + g*(1-depth),
                         128*depth + b*(1-depth),
                         a))
  return ret_val

class depth_img:
  def __init__(self, name):
    img = pygame.image.load('gfx/'+name+'.png')
    self.d = [ fade(img, i/8.0).convert_alpha()
               for i in xrange(8) ]

  def level(self, lev):
    if lev < 0: return self.d[0]
    if lev > 7: return self.d[7]
    return self.d[lev]



#typeahead command examples.  Applies to the selected area.
#'excavate'
#'mine [for <material>] [and deliver to <place>]'
#'fill [with <material>]'
#'move [<object type>] to <place>'
#'build [<thing>]'
#'evacuate [to <place>]'
#'finish walls'
#'clean up'

#modifiers:
#', <dwarf name>/everyone'
#'with priority <number>'

#display with icons for each dwarf, and a number indicating the
#priority of the current task?


class dagger_io:
  def main(self):
    clock = pygame.time.Clock()

    (ox, oy, oz) = (0, 0, 0)

    csr = gfx.block_3d(gfx.mark1, 0, 0, 0, pri=1)

    for ix in range(-5,30):
      for iy in range(-5,30):
        world.world(ix,iy,0)

    while 1:
      clock.tick(35)

      for event in pygame.event.get():
        if event.type == QUIT: return
        elif event.type == KEYDOWN:
          if event.key == K_ESCAPE:
            return
          if event.key == K_LEFT:
            csr.move(-1,0,0)
          elif event.key == K_RIGHT:
            csr.move(1,0,0)
          elif event.key == K_UP:
            csr.move(0,1,0)
          elif event.key == K_DOWN:
            csr.move(0,-1,0)
          elif event.unicode == '.':
            csr.move(0,0,-1)
          elif event.unicode == ',':
            csr.move(0,0,1)
          elif event.unicode == ' ':
            world.world.invert(csr.x, csr.y, csr.z)
          elif event.unicode == '1':
            (ox, oy, oz) = (csr.x, csr.y, csr.z)
          elif event.unicode == '2':
            fill = (world.world(csr.x, csr.y, csr.z) == None)
            for ix in range(min(ox, csr.x), max(ox, csr.x)+1):
              for iy in range(min(oy, csr.y), max(oy, csr.y)+1):
                for iz in range(min(oz, csr.z), max(oz, csr.z)+1):
                  if fill:
                    world.world.construct(ix,iy,iz)
                  else:
                    world.world.dig(ix,iy,iz)
                              
          else:
            print event.key, event
            print clock.get_fps()
            
      gfx.paint_frame()

#      screen.blit(background, (0,0))
#      for z in range(7,-1+csr.z,-1):
#        for x in xrange(25):
#          for y in xrange(24,-1,-1):
#            w_loc = 24 * x + 12 * y
#            h_loc = 12 * x - 24 * y + 13 * z + 400
#            if (csr.z, csr.x, csr.y) == (z, x, y):
#              screen.blit(self.cursor_bot_img.level(0),
#                               (w_loc, h_loc))
#            if world[x][y][z] == 1:
#              screen.blit(self.block_img.level(z),
#                               (w_loc, h_loc))
#            if (csr.z, csr.x, csr.y) == (z, x, y):
#              screen.blit(self.cursor_top_img.level(0),
#                               (w_loc, h_loc))
#
#      pygame.display.flip()


if __name__ == '__main__': dagger_io().main()
