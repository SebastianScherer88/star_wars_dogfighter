# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 21:02:34 2018

@author: bettmensch
"""

import pygame as pg
import os
import sys

os.getcwd()

pg.init()

# [0] create surfaces

# create surface form image
loaded_image = pg.image.load("./graphics/misc/ally_frame.bmp") # creates a 45X40X24 surface | 24 is the color channel number; apparently it was saved as a 24 bmp
# to convert to 32 channel:
# - create main screen by calling pygame.display.set_mode() - creates&returns a 32 channeld surface by defualt
# - call loaded_image.convert() - converts&returns 32 channel (the same as main screen) formatted version of loaded_image surface
#
# Note that this was not done to get below results

image_dims = loaded_image.get_size()

# create surface using pygame's Surface object, then blit image to it
created_surface = pg.Surface((image_dims[0]+20,image_dims[1]+20)) # created a 45X40X32 surface | 32 is the color channel number; apparently 32 is the default
created_surface.blit(loaded_image,(10,10))


# [1] get colorkeys from both default surfaces

loaded_colorkey = loaded_image.get_colorkey()
created_colorkey = created_surface.get_colorkey()

print(loaded_colorkey) # None
print(created_colorkey) # None

# [2] make created surface white (255,255,255); set colorkey to white for obth surfaces & compare again

WHITE = (255,255,255)

#created_surface.fill(WHITE)

# set colorkeys
loaded_image.set_colorkey(WHITE)
created_surface.set_colorkey(WHITE)

# get colorkeys
loaded_colorkey = loaded_image.get_colorkey()
created_colorkey = created_surface.get_colorkey()

print(loaded_colorkey) # (255255,255,255)
print(created_colorkey) # (255,255,255)

# [3] Blit both surfaces to a black screen

SCREEN_SIZE = (400,400)
PINK = (255,0,255)

# create black main screen
main_screen = pg.display.set_mode(SCREEN_SIZE)
main_screen.fill(PINK)

# blit loaded surface
main_screen.blit(loaded_image,(150,200))

# blit created surface
main_screen.blit(created_surface,(250,200)) # -> both sprite images appear transparent

pg.display.flip()

# end screen mode
pg.quit()
sys.exit()