# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 21:41:38 2018

@author: bettmensch
"""

'''This script classes representing weapon objects in the game STAR WARS DOGFIGHTER.
For now it only contains the experimental LaserWeapon class and the ProjectileSprite class
representing laser beams (and possibly other projectiles in the future).'''

from animation_classes import TrackingAnimation
from basic_sprite_classes import BasicSprite
from math import sin,cos,pi

import pygame as pg
import numpy as np

class ProjectileSprite(BasicSprite):
    '''Class used for projectiles fired by player or enemy sprites.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 lifetime_in_seconds,
                 groups,
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
            lifetime: lifetime pf sprite (in seconds).
            groups: tuple of pygame Group objects. The sprite will add itself to each of these
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
                                               
        # initialize and add to groups if sensible
        BasicSprite.__init__(self,
                             fps,
                             screen,
                             original_images,
                             groups,
                             center=center,
                             angle=angle,
                             speed=speed,
                             is_transparent=is_transparent,
                             transparent_color=transparent_color)
        
        # set lifetime related attributes
        self._lifetime_in_frames = fps * lifetime_in_seconds
        self.frames_passed = 0
        
    def update(self):
        '''BasicSprite update method plus checks & handling against MissileSprite's
        lifetime  attribute.'''
        
        # call base class update
        BasicSprite.update(self)
        
        # update frame counter
        self.frames_passed += 1
                    
        # if life time is over, terminate MissileSprite
        if self.frames_passed > self._lifetime_in_frames:
            self.kill()


class LaserCannon(object):
    '''This class represents a ship's laser cannon. One or more instances of this 
    class will be attached to each ship that carries weapons. The LaserWeapon class
    allows for outsourcing the firing process so as not to overload the ShipSprite 
    class. It can check whether it's ready to fire based on an individual firing rate,
    creates the laser beam and the muzzle flash animation.'''
    
    def __init__(self,
                 ship_sprite=None,
                 cannon_offset=None,
                 cannon_fire_rate=1,
                 cannon_range_in_seconds=1.5,
                 cannon_projectile_speed_in_seconds=200,
                 cannon_projectile_group=None,
                 original_laser_beam_images=None,
                 original_muzzle_flash_images=None,
                 muzzle_flash_animation_spi=0.03):
        '''Initializer of LaserWeapon class object.
        Arguments:
            - ship_sprite: ShipSprite class object. Parent ship to which the laser
            weapon is attached. Needed to access positional and angle parameters
            at firing time.
            - cannon_fire_rate: rate of fire for this laser weapon, in shots/second
            - cannon_offset: 2-dim offset vector specifying the laser weapon tip w.r.t
            the parent ship sprite's center position. needed to align the laser beam
            and muzzle flash animations with the ship sprite's on screen skin.
            - cannon_range_in_seconds: how long the laser beam (class MissileSprite object)
            created by this object class at firing time will stay alive in seconds.
            - cannon_projectile_speed_in_seconds: the speed of the laser beam in pixel per second
            if shot from a stationary ship sprite.
            - cannon_projectile_group: Laser beam sprites will be added to this group.
            - original_laser_beam_images: pygame surface object specifiying the laser beam
            design at 0 degrees orientation.
            - original_muzzle_flash_images: list of pygame surface objects specifiying the
            laser muzzle flash animation (at 0 degrees orientation).
            - muzzle_flash_animation_spi: seconds per image for muzzla flash animation.'''
            
        # attach parent sprite
        self._ship = ship_sprite
        
        # attach laser group
        self._laser_beam_group = cannon_projectile_group
        
        # attach mechanic weapon specs
        self._offset = np.array(cannon_offset)
        self._rate_of_fire = cannon_fire_rate
        self._range_in_seconds = cannon_range_in_seconds
        self._projectile_speed_in_seconds = cannon_projectile_speed_in_seconds
        
        # attach original laser image
        self._original_laser_beam_images = original_laser_beam_images
        
        # attach original muzzle flash animation image sequence and spi
        self._original_muzzle_flash_images = original_muzzle_flash_images
        self._muzzle_flash_spi = muzzle_flash_animation_spi
        
        # initialize time of last shot that weapon is ready after initializion
        self._time_of_last_shot = pg.time.get_ticks() - 1005 / cannon_fire_rate # 1005 -> milliseconds unit and + epsilon
        
    def is_ready(self):
        '''Util function called from ship to assess weapon state. Return True if 
        ready to fire, else False.'''
        
        return (pg.time.get_ticks() - self._time_of_last_shot) > 1000 / self._rate_of_fire
    
    def get_laser_beam_positions(self):
        '''Calculates the coordinates of the ship sprite's gun tips w.r.t the main
        game screen's coordinate system as a 2x1 array. Also calculates the rotated
        offset (based on ship sprite's current angle) w.r.t ship sprite's image's 
        center.'''
        
        # convert ship's current angle to radian
        radian_angle = self._ship._angle * pi / 180
        
        # get rotation matrix for radian angle
        rotation_matrix = np.array([[cos(radian_angle), sin(radian_angle)],
                                   [- sin(radian_angle), cos(radian_angle)]])
            
        # rotate offsets and add to ship's center
        rotated_position = np.dot(rotation_matrix,
                                  self._offset.T).T + self._ship._center
        
        return rotated_position
    
    def fire(self):
        '''Util function called from ship to fire cannon. Calculates necessary offsets, then
        creates a laser beam (class MissileSprite object) and a muzzle flash animation (class
        TrackingAnimation object) at appropriate main game screen position.'''
        
        # get: main game screen coordinates for laser beams, offsets for muzzle flash
        laser_beam_position = self.get_laser_beam_positions()
        
        # create muzzle flash
        TrackingAnimation(self._ship._fps,
                          self._ship._screen,
                          self._original_muzzle_flash_images,
                          self._muzzle_flash_spi,
                          self._ship,
                          self._offset,
                          [self._laser_beam_group])
        
        # create laser beam
        ProjectileSprite(self._ship._fps,
                      self._ship._screen,
                     self._original_laser_beam_images,
                     self._range_in_seconds,
                     [self._laser_beam_group],
                     center = laser_beam_position,
                     angle = self._ship._angle,
                     speed = self._ship._speed * self._ship._fps + self._projectile_speed_in_seconds)
        
        # update time of last shot attribute
        self._time_of_last_shot = pg.time.get_ticks()