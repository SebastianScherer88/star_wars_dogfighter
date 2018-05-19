# -*- coding: utf-8 -*-
"""
Created on Sat May 19 22:36:56 2018

@author: bettmensch
"""

'''This file contains the sprite classes used in the game STAR WARS DOGFIGHTER.
It contains the 'MaskedSprite' class which functions as a functional base class
for the more refined custom classes 'PlayerSprite', 'EnemySprite' and 'LaserSprite'.'''

from pygame.sprite import Sprite, Group
from math import cos, sin

import pygame as pg
import numpy as np

class MaskedSprite(Sprite):
    
    def __init__(self,image_path,*groups,**initial_values):
        '''image: path to sprite image
        *groups: optional (unnamed) list of groups the sprite will be added to
                          when created
        **initial_values: Options are angle, speed, left and top. Allows specific
                            placement/orientation/status at creation'''
                            
        # initialize and add to groups if sensible
        Sprite.__init__(self,*groups)

        # get and attach image as pygame surface
        self.image = pg.image.load(image_path)
        
        # get and attach positional rectangle
        self.rect = self.image.get_rect()
        
        # get and attach mask
        self.mask = pg.mask.from_surface(self.image)
        
        # set default initial values where necessary
        self.speed = 0
        self.angle = 0
        self.rect.left = 0
        self.rect.top = 0
        
        # work through initial values if sensible
        if 'angle' in initial_values.keys():
            self.rotate(initial_values['angle'])
        if 'speed' in initial_values.keys():
            self.speed = initial_values['speed']
        if 'left' in initial_values.keys():
            self.rect.left = initial_values['left']
        if 'top' in initial_values.keys():
            self.rect.top = initial_values['top']
        
    def rotate_ip(self,d_angle):
        '''Rotates the sprite in place by differential angle d_angle. Updates the image,
        rect and angle attribute accordingly.'''
        
        if d_angle == 0:
            # do nothing
            pass
        else:
            # rotate sprite image
            self.image = pg.transform.rotate(self.image,d_angle)
            
            # update the positional rect
            self.rect = self.image.get_rect()
            
            # update mask
            self.mask = pg.mask.from_surface(self.image)
            
            # update angle
            self.angle += d_angle
            
    def move_ip(self,d_speed):
        '''Moves the sprite in place. Takes a differential speed d_speed and calculates
        new speed if necessary. Then calculates the unit direction vector based
        on current angle nad moves the sprite accordingly.'''
        
        if d_speed != 0:
            # update speed
            self.speed += d_speed
            
        # get velocity vector
        velocity = np.array([cos(self.angle),sin(self.angle)]) * self.speed
        
        # move sprite by moving sprite's rect attribute
        self.rect = self.rect.move(velocity[0],velocity[1])
        
class PlayerSprite(MaskedSprite):
        
    d_angle = 5
    d_speed = 2
    max_speed = 20
        
    def get_player_input(self):
        '''Gets player control input and converts into angle and speed
        differentials d_angle and d_speed, as well as fire command.'''
            
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
            
        # get angle differential
        if pressed_keys[pg.K_LEFT] and not pressed_keys[pg.K_RIGHT]:
            d_angle = self.__class__.d_angle
        elif pressed_keys[pg.K_RIGHT] and not pressed_keys[pg.K_LEFT]:
            d_angle = -self.__class__.d_angle
        else:
            d_angle = 0
            
        # get speed differential
        if pressed_keys[pg.K_UP] and not pressed_keys[pg.K_DOWN]:
            d_speed = min(self.__class__.d_speed,self.__class__.max_speed - self.speed)
        elif pressed_keys[pg.K_DOWN] and not pressed_keys[pg.K_UP]:
            d_speed = -min(self.__class__.d_speed,self.speed)
        else:
            d_speed = 0
            
        # get fire command
        if pressed_keys[pg.K_SPACE]:
            fire_cannon = True
        else:
            fire_cannon = False
            
        return d_angle, d_speed, fire_cannon
    
    def update(self):
        '''Updates the sprites position based on player control input. Also fires
        cannon when necessary.'''
        
        # handle player controls
        d_angle, d_speed, fire_cannon = self.get_player_input()
            
        # rotate sprite if necessary
        self.rotate_ip(d_angle)
        
        # move player sprite
        self.move_ip(d_speed)
            
        # fire cannon
        if fire_cannon:
            print('FIRE THE CANNON!')
            
# demo gam states here
import sys, pygame, os

os.chdir('C:\\Users\\bettmensch\\GitReps\\star_wars_dogfighter')

pygame.init()

# create clock    
clock = pg.time.Clock()

white = 255, 255, 255
fps = 40

# initialize main screen
size = width, height = 620, 540 # screen size
screen = pg.display.set_mode(size)

player_sprite = Group()

player = PlayerSprite('.\\graphics\\ship.bmp',player_sprite)
               
while 1:
    # check for exit events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    
    # update all sprites
    player_sprite.update()

    # draw new game state    
    screen.fill(white) # paint over old game state
    player_sprite.draw(screen) # draw all sprites in updated states/positions    
               
    # flip canvas
    pg.display.flip()
    
    # control pace
    clock.tick(fps)