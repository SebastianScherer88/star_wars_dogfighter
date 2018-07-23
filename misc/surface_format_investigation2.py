# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 21:19:59 2018

@author: bettmensch
"""

import sys
import os
import pygame as pg

# [0] initialize pygame

BLACK = (0,0,0)
YELLOW = (255,255,0)

pg.init()
main_screen = pg.display.set_mode((400,400))
main_screen.fill(YELLOW)

# [1] build visual surface

WHITE = (255,255,255)

# make transparent sprite image
loaded_sprite_image = pg.image.load("./graphics/sprite_skins/xwing.bmp") # creates a 45x40x24 surface | 24 is the color channel, induced by .bmp format
loaded_sprite_image.set_colorkey(WHITE)
sprite_alpha = loaded_sprite_image.get_alpha()
print(sprite_alpha)


loaded_frame_image = pg.image.load("./graphics/misc/hostile_frame.bmp") # creates a 50X50X24 surface | 24 is the color channel number; apparently it was saved as a 24 bmp
loaded_frame_image.set_colorkey(WHITE)
frame_alpha = loaded_frame_image.get_alpha()
print(frame_alpha)

canvas = pg.Surface((70,70)) # creates 70x70x32 surface | 32 is the color channel, pygame default
canvas_alpha = canvas.get_alpha()
print(canvas_alpha)

canvas.fill(BLACK)
canvas.set_colorkey(BLACK)


# start blitting to canvas
canvas.blit(loaded_sprite_image,(15,15)) # blit sprite image
canvas.blit(loaded_frame_image,(10,10)) # blit frame (over sprite image)

# [2] draw tp main screen and show

# create background image
background_sprite = pg.image.load("./graphics/sprite_skins/awing.bmp")
main_screen.blit(background_sprite,(95,95))

# put canvas in shop window
main_screen.blit(canvas,(100,100))

# open blinds
pg.display.flip()

# [-1] end it
pg.quit()
sys.exit()