# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 00:04:44 2018

@author: bettmensch
"""

from pygame.sprite import Sprite
from math import cos, sin, pi

import pygame as pg
import numpy as np

class BasicSprite(Sprite):
    '''Base class for all masked sprites that appear in the game.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 is_transparent = True,
                 transparent_color = (255,255,255)):
        
        '''Arguments:
            
            fps: frames per second ratio of surrounding pygame
             screen: the main screen the game is displayed on (pygame Surface).
                    Needed to 'wrap' sprites around edges to produce 'donut topology'.
            original_images: list of surface objects that will be used to display the sprite.
                    By default, the first list element will be used.
            *groups: tuple of pygame Group objects. The sprite will add itself to each of these
                    when initialized.
            center: initial position of center of sprite's rectangle (numpy float-type array of shape (2,)).
                    Sets the sprite's initial position on the 'screen' surface.
            angle: initial orientation of sprite in degrees. Angle is taken counter-clockwise, with
                    an angle of zero meaning no rotation of the original surface.
            speed: initial speed of sprite (pixels per second). scaler of float type.
                    Default is 0.
            is_transparent: transparency flag. If set, pixels colored in the 'transparent_color'
                    color argument in the surfaces contained in 'original_images' will be made transparent.
                    Default is True
            transparent_color: tuple specifiying the color key considered as transparent if 'is_transparent'
                    is set to true. Default to (255,255,255), which corresponds to the color white.'''
                    
        # call Sprite base class init - add self to all groups specified
        Sprite.__init__(self,*groups)
        
        # set surrounding pygame variables as attributes
        self._screen = screen
        self._fps = fps
        
        # if necessary, make original image surfaces transparent; then attach
        if is_transparent:
            for original_image in original_images:
                original_image.set_colorkey(transparent_color)
                
        self._original_images = original_images
        
        # set positional attributes using initial values passed
        self._center = np.array(center,dtype='float')
        self._angle = angle
        self._speed = speed / fps # convert to pixel per frame
        
        # set rate of change of positional attributes
        self._d_angle = 0
        self._d_speed = 0
        
        # set sprite up
        # set image and rect - these will be called by Group object methods; get mask
        self._image_index = 0 # always start with first image in original_images

        # initialize image surface object
        self._size_factor = 1
        self.image = pg.transform.rotozoom(self._original_images[self._image_index],
                                           self._angle,
                                           self._size_factor)
        
        # update object type attribute: mask
        self.mask = pg.mask.from_surface(self.image)
        
        # update object type attributes: positional rectangle
        self.rect = self.image.get_rect()
        
        self.rect.center = self._center
        
    def update_positional_attributes(self):
        '''Updates the sprites positional attributes '_angle' and '_speed'.
        Does not update the 'image','rect' or 'mask' attributes.'''
        
        # update angle argument
        self._angle += self._d_angle
        
        # update speed argument
        self._speed += self._d_speed
        
        # control speed
        self._control_speed()
        
        # update center argument
        self._center += self.get_velocity_vector()
        
        # get main screen and current sprite image's dimensions for wrap checks
        screen_w, screen_h= self._screen.get_size()
        image_w, image_h = self.image.get_size()
        
        # wrap horizontaly if needed
        if self._center[0] < - image_w / 2:
            self._center[0] = screen_w + image_w / 2
        elif self._center[0] > screen_w + image_w / 2:
            self._center[0] = - image_w / 2
                        
        # wrap vertically if needed
        if self._center[1] < - image_h / 2:
            self._center[1] = screen_h + image_h / 2
        elif self._center[1] > screen_h + image_h / 2:
            self._center[1] = - image_h / 2
            
        
    def get_velocity_vector(self):
        '''Calculates a 2-dim velocity vector (units: frames per second) based
        on 'self._angle' and 'self._speed' attributes.'''
        
        # convert angle to radian
        radian_angle = self._angle * pi / 180
        
        # compute velocity vector
        velocity = self._speed * np.array([cos(radian_angle),
                                           -sin(radian_angle)]).reshape((1,2)) # in pygame coordinates, the y-axis has negative orientation
        
        return velocity.reshape(2)
    
    def set_pilot_commands(self):
        '''Calculates and sets the scalar float values for attributes  _d_angle
        and _d_speed. For this base class, it does nothing, but can be edited
        in more sophisticated classes to effectively implement an AI pilot.'''
        
        return
    
    def _control_speed(self):
        '''Util function that ensures sprite respects its speed constraints.
        Only used at ShipSprite (and upwards) level.'''
        
        return
        
    
    def update(self):
        '''Updates the sprite's object type attributes 'image','rect' and 'mask' based on 
        updated numerical positional attributes'self._angle','self._speed' and self_center'.'''
        
        # get directional changes
        self.set_pilot_commands()
        
        # update numerical positional attributes
        self.update_positional_attributes()
        
        # update object type attributes: surface
        self.image = pg.transform.rotozoom(self._original_images[self._image_index],
                                           self._angle,
                                           self._size_factor)

        # update object type attribute: mask
        self.mask = pg.mask.from_surface(self.image)
        
        # update object type attributes: positional rectangle
        self.rect = self.image.get_rect()
        self.rect.center = self._center
