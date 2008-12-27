import pygame
from pygame.locals import *

def load_img(name):
  return pygame.image.load('gfx/'+name+'.png').convert_alpha()

pygame.init()

screen = pygame.display.set_mode((800,800))

block = load_img('block')
block_s1 = load_img('block_s1')
block_s2 = load_img('block_s2')
block_s3 = load_img('block_s3')
virt_block = load_img('virt_block')
mark1 = load_img('mark1')
selbot = load_img('sel.bot')
seltop = load_img('sel.top')
selleft = load_img('sel.left')
selright = load_img('sel.right')
selfront = load_img('sel.front')
selback = load_img('sel.back')


pygame.display.set_caption('Dagger')
pygame.mouse.set_visible(1)

background = pygame.Surface(screen.get_size()).convert()
background.fill((128,128,128))

screen.blit(background, (0,0))

dirty_rects = []
visible = pygame.sprite.Group()

def paint_frame():
  global dirty_rects
  pygame.display.update(dirty_rects)
  #pygame.display.flip()
  dirty_rects = []

def refresh_rect(r):
  global dirty_rects, background

  dirty_sprites = []
  all_sprites = visible.sprites()
  for s in r.collidelistall(all_sprites):
    dirty_sprites.append(all_sprites[s])

  dirty_sprites.sort(cmp=paint_order)

  screen.set_clip(r)

  screen.blit(background, r, r)

  for paintme in dirty_sprites:
    screen.blit(paintme.image, paintme.rect)
    
  screen.set_clip(None)
      
  dirty_rects.append(r)

sel_sprites = []

def paint_selection(s, e):
  global sel_sprites
  for sprite in sel_sprites:
    sprite.delete()
  sel_sprites = []

  print s, e
  
  sx, sy, sz = s
  ex, ey, ez = e
  xr = xrange(min(sx, ex), max(sx, ex)+1)
  yr = xrange(min(sy, ey), max(sy, ey)+1)
  zr = xrange(min(sz, ez), max(sz, ez)+1)

  for (xrn, yrn, zrn, pic, pri) in ( #generate an iteration for each side
    [ (xr, yr, [zr[0]], selbot, -1),
      (xr, yr, [zr[-1]], seltop, 1),
      (xr, [yr[0]], zr, selfront, 1),
      (xr, [yr[-1]], zr, selback, -1),
      ([xr[0]], yr, zr, selleft, -1),
      ([xr[-1]], yr, zr, selright, 1) ]):
    for x in xrn:
      for y in yrn:
        for z in zrn:
          sel_sprites.append(sprite_3d(pic, x, y, z, pri))
          

def paint_order(a, b):
  if a.z != b.z:
    return a.z - b.z
  if a.x != b.x:
    return a.x - b.x
  if a.y != b.y:
    return b.y - a.y
  
  return a.pri - b.pri

class sprite_3d(pygame.sprite.Sprite):
  def __init__(self, image, x, y, z, pri=0):
    global background
    pygame.sprite.Sprite.__init__(self)
    self.x = x; self.y = y; self.z = z;
    self.pri = pri
    self.image = image
    self.rect = image.get_rect().move(24*x + 12*y,
                                      12*x - 24*y - 13*z + 600)
    if self.rect.colliderect(background.get_rect()):
      visible.add(self)
    self.repaint()

  def move(self, rx, ry, rz):
    self.x += rx; self.y += ry; self.z += rz
    old_rect = self.rect
    self.rect = self.image.get_rect().move(24*self.x + 12*self.y,
                                           12*self.x - 24*self.y - 13*self.z + 600)
    refresh_rect(old_rect)
    refresh_rect(self.rect)    
    
  def repaint(self):
    """Repaint the rectange we occupy."""
    refresh_rect(self.rect)

  def delete(self):
    visible.remove(self)
    self.repaint()
