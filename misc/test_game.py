# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 11:29:17 2018

@author: bettmensch
"""

import pygame as pg
import sys

pg.init()

# create clock object
clock = pg.time.Clock()

# set pygamw window size
size = (400,400)

# get pygame window
main_screen = pg.display.set_mode(size)
main_screen.fill((255,255,255))

# set caption for pygame window
pg.display.set_caption("Test game for conversion to executable file")

# initialize player block parameters
x, y = 0, 0 # position
dx, dy = 0, 0 # speed

# start main game loop
while True:
    # handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # quit pygame
            pg.quit()
            sys.exit()
                    
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                # quit pygame
                pg.quit()
                sys.exit()
                
            if event.key == pg.K_UP:
                # do  something
                dy -= 5
            if event.key == pg.K_DOWN:
                # do  something
                dy += 5
            if event.key == pg.K_LEFT:
                # do  something
                dx -= 5
            if event.key == pg.K_RIGHT:
                # do  something
                dx += 5
                
        if event.type == pg.KEYUP:
            if event.key == pg.K_UP:
                # do  something
                dy += 5
            if event.key == pg.K_DOWN:
                # do  something
                dy -= 5
            if event.key == pg.K_LEFT:
                # do  something
                dx += 5
            if event.key == pg.K_RIGHT:
                # do  something
                dx -= 5
                
    # update player position
    x += dx
    y += dy
    
    # fill main surface with white
    main_screen.fill((255,255,255))
    
    # draw player
    pg.draw.rect(main_screen, (0,0,0), (x,y,20,20))
    
    # flip canvas
    pg.display.flip()
    
    # control game speed
    clock.tick(20)