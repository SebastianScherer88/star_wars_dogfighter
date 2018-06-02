# -*- coding: utf-8 -*-
"""
Created on Sat May 19 22:36:56 2018

@author: bettmensch
"""

'''This file contains the sprite classes used in the game STAR WARS DOGFIGHTER.
It contains the \'MaskedSprite\' class which functions as a functional base class
for all viewable sprite objects in the game.
The FighterSprite class serves as a sub-base class for the spaceship/fighter plane
sprites (either player or pc controlled) \'PlayerSprite\' and \'EnemySprite\'.
The \'LaserSprite\' class is based directly on the MaskedSprite class.'''

from pygame.sprite import Sprite
from math import cos, sin, pi

import pygame as pg
import numpy as np

class MaskedSprite(Sprite):
    
    def __init__(self,
                 screen,
                 sprite_meta_data,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.array([0,0]).astype('float')):
        '''image: path to sprite image
        *groups: optional (unnamed) list of groups the sprite will be added to
                          when created
        **initial_values: Options are angle, speed, left and top. Allows specific
                            placement/orientation/status at creation'''
                            
        # initialize and add to groups if sensible
        Sprite.__init__(self,*groups)
        
        # attach screen
        self.screen = screen
        
        # retrieve sprite meta data
        self.meta_data = sprite_meta_data
        
        # load and attach the animation sequence's images
        self._original_images = []
        
        for image_path in sprite_meta_data['image_paths']:
            image = pg.image.load(image_path)
            image.set_colorkey((255,255,255))
            self._original_images.append(image)     
        
        # set default initial values where necessary
        self._speed = speed # needed to keep track of speed
        self._angle = angle # needed to kepp track of angle
        self._center = center # needed to recenter image after rotation
            
        # initialize image _index
        self.image_index = 0
            
        # get temporary image
        self.image = pg.transform.rotate(self._original_images[self.image_index],
                                         self._angle)
        
        # get and attach mask
        self.mask = pg.mask.from_surface(self.image)
        
        # get and attach positional rectangle
        self.rect = self.image.get_rect()
        self.rect.center = self._center
            
        
    def rotate_ip(self,d_angle):
        '''Rotates the sprite in place based on differential angle d_angle. Updates
        the image, rect and angle attribute accordingly.'''
        
        # get new angle
        self._angle += d_angle
        
        # rotate sprite image by angle
        self.image = pg.transform.rotate(self._original_images[self.image_index],
                                         self._angle)
        
        # update the positional rect
        self.rect = self.image.get_rect()
        self.rect.center = self._center
        
        # update mask
        self.mask = pg.mask.from_surface(self.image)
            
    def move_ip(self,d_speed):
        '''Moves the sprite in place. Takes a differential speed d_speed and calculates
        new speed if necessary. Then calculates the unit direction vector based
        on current angle nad moves the sprite accordingly.'''
        
        # get new speed (might be old speed if d_speed = 0)
        self._speed += d_speed
        
        # convert self._angle attribute to radian for cos & sin functions
        angle_radian = self._angle * pi / 180
            
        # get velocity vector
        velocity = np.array([cos(angle_radian),-sin(angle_radian)]) * self._speed
        
        # move sprite by moving sprite's _center attribute and updating rect
        # (necessary bc floats smaller than 1 get rounded)
        self._center += velocity
        self.rect.center = self._center

        # wrap around screen edges if necessary  
        screen_width  = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        if self.rect.left > screen_width:
            self._center[0] = -self.rect.width / 2 # equivalent of setting rect.right = 0, analogous for the other cases
        elif self.rect.right  < 0:
            self._center[0] = screen_width + self.rect.width / 2
        if self.rect.bottom < 0:
            self._center[1] = screen_height + self.rect.height / 2
        elif self.rect.top > screen_height:
            self._center[1] = 0 - self.rect.height / 2
                        
        
class FighterSprite(MaskedSprite):
    '''Parent class for PlayerSprite and EnemySprite. Allows for a slim MaskedSprite
    class that has doesnt lead to 'appendix syndrome' for the LaserSprite class.'''
    
    gun_muzzle_flash_frames = 10 # number of frames the gun muzzle flare should be visible after firing
    
    def __init__(self,screen,sprite_meta_data,laser_meta_data,laser_beams_group,*groups,**initial_values):
        
        # call parent class __init__
        MaskedSprite.__init__(self,screen,sprite_meta_data,*groups,**initial_values)
        
        # set meta attibutes dependent on chosen fighter type
        self._d_angle = self.meta_data['rotation_speed'] # rotation rate for this ship type (in degrees)
        self._d_speed = self.meta_data['acceleration'] # acceleration rate for this ship type
        self._max_speed = self.meta_data['max_speed'] # max speed for this ship type
        self._laser_speed = self.meta_data['laser_speed'] # laser speed is constant across all shiptypes
        self._laser_lifetime = self.meta_data['laser_lifetime'] # laser lifetime is constant across all ship types
        self._weapon_cool_down = self.meta_data['weapon_cool_down'] # number of frames between shots
        self._rel_cannon_tip_positions = self.meta_data['cannon_tip_positions'] # pixel coordinates of gun tips relative to image center
        
        # attach laser beam meta data
        self.laser_meta_data = laser_meta_data
                                                       
        # attach laser beam 'basket' group
        self.laser_beams = laser_beams_group
        
        # set the weapon cool down counter
        self.weapon_cooling = 0
        
        # set the muzzle flare counter
        self.muzzle_flash_counter = 0
        
    def get_pilot_commands(self):
        '''Controls the sprites steering process. Either player or 'AI' controlled.
        Returns:
            - d_angle: float that indicates angle w.r.t current direction, i.e.
                        '0' to go straight on. Positive values lead to left turns,
                        negative value to right turns
            - d_speed: float that indicates acceleration on a per frame basis.
                        Probably only relevant for player controlled sprite. Positive
                        acceleration means speeding up, negative means slowing down.'''
                        
    def get_gunner_commands(self):
        ''' Controls the sprites weapon firing process. Either player or 'AI' controlled.
        Returns:
            - fire_cannon: Bool. 'True' to fire laser, 'False' to not.'''
            
    def _get_gun_muzzle_positions(self,sprite_surface=False):
        '''Calculates pixel tuple specifiying the location of the current sprite's
        gun tips.'''
        
        # construct rotational matrix to apply to gun tips positional array
        laser_angle_radian = self._angle * pi / 180
        
        rotation_matrix = np.array([[cos(laser_angle_radian), sin(laser_angle_radian)],
                                   [- sin(laser_angle_radian), cos(laser_angle_radian)]])
        
        # rotate relative gun tip positions around center of image
        rotated_rel_gun_muzzle_positions = np.dot(rotation_matrix,
                                                  self._rel_cannon_tip_positions.T).T
        
        # make sure to get correct kind of position, i.e. absolute or relative
        if sprite_surface:
            # take the positions of gun muzzles w.r.t. to the center of the sprite positional rect
            sprite_surface_center = np.array(self.image.get_size()).reshape((1,-1))
            gun_muzzle_positions = sprite_surface_center / 2 + rotated_rel_gun_muzzle_positions
        if not sprite_surface:
            # add sprite center coordinates to relative gun tip coordinates absolute gun muzzle positions
            gun_muzzle_positions = self._center + rotated_rel_gun_muzzle_positions
        
        #return gun_tip_positions
        
        return gun_muzzle_positions
        
            
    def draw_gun_muzzle_flash(self):
        '''temporary drawing function to help evaluate current gun tip location
        calculation approach implemented in the "get_guntips_positions()" method.'''
        
        # iterate through sprites gun muzzle positions 
        for gun_muzzle_position in self._get_gun_muzzle_positions(sprite_surface=True):
            # draw a flash for each gun muzzle onto sprite surface
            pg.draw.circle(self.image,
                           (255,0,0), # red
                           gun_muzzle_position.astype('int'), # pygame drawing functions only accept integer pixel positions
                           2)
        
            
    def fire_cannon(self):
        '''Fires the cannon if firing flag 'fire_cannon' is True by creating a
        LaserSprite object with appropriate initial values near sprite's cannon
        guns' tips. Reset weapon cool down counter when necessary.'''
        
        # fire laser beam: set arguments for laser __init__
        laser_screen = self.screen
        laser_lifetime = self._laser_lifetime
        laser_speed = self._speed + self._laser_speed
        laser_angle = self._angle
        
        # fire laser beam: create laserSprite instance
        for gun_muzzle_position in self._get_gun_muzzle_positions():
            # set gun muzzle countdown to maximum so that sprite's draw method will draw the flares
            self.muzzle_flash_counter = self.__class__.gun_muzzle_flash_frames
            
            print('fire!')
            
            # spawn laser at gun tip
            LaserSprite(laser_screen,
                        self.laser_meta_data,
                        laser_lifetime,
                        self.laser_beams,
                        speed=laser_speed,
                        angle=laser_angle,
                        center=tuple(gun_muzzle_position))
            
        # set cool down counter to maximum after weapon use
        self.weapon_cooling = self._weapon_cool_down
        
            
    def update(self):
        '''Updates the sprites position based on player control input. Also fires
        cannon when necessary.'''
        
        # handle pilot controls
        d_angle, d_speed = self.get_pilot_commands()
        
        # handle gunner controls
        fire_cannon = self.get_gunner_commands()
            
        # rotate sprite if necessary
        if d_angle != 0:
            self.rotate_ip(d_angle)
        
        # move sprite
        self.move_ip(d_speed)
            
        # fire cannon if necessary
        if fire_cannon and not self.weapon_cooling:
            self.fire_cannon()
            
        # update the gun muzzle flash counter and draw flashes if necessary
        if self.muzzle_flash_counter > 0:
            self.draw_gun_muzzle_flash() # draw the flashes
            self.muzzle_flash_counter -= 1 # update the flash countdown
        elif self.muzzle_flash_counter == 0:
            # refresh sprite surface, wiping off any remaining gun flashes
            self.image = pg.transform.rotate(self._original_images[self.image_index],
                                             self._angle)
        
        # update weapon cooling counter but keep at minimum 0
        if self.weapon_cooling > 0:
            self.weapon_cooling -= 1
    

class PlayerSprite(FighterSprite):
    '''Class used for player fighter.'''
        
    def get_pilot_commands(self):
        '''See parent class 'FighterSprite' method doc.'''
        
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
            
        # get angle differential
        if pressed_keys[pg.K_LEFT] and not pressed_keys[pg.K_RIGHT]:
            d_angle = self._d_angle
        elif pressed_keys[pg.K_RIGHT] and not pressed_keys[pg.K_LEFT]:
            d_angle = -self._d_angle
        else:
            d_angle = 0
            
        # get speed differential
        if pressed_keys[pg.K_UP] and not pressed_keys[pg.K_DOWN]:
            # dont accelerate above sprite's max speed
            d_speed = min(self._d_speed,self._max_speed - self._speed)
        elif pressed_keys[pg.K_DOWN] and not pressed_keys[pg.K_UP]:
            # dont decelarate to going backwards
            d_speed = -min(self._d_speed,self._speed)
        else:
            d_speed = 0
            
        return d_angle, d_speed
    
    def get_gunner_commands(self):
        '''See parent class 'FighterSprite' method doc.'''
        
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
        
        # get fire command
        if pressed_keys[pg.K_SPACE]:
            fire_cannon = True
        else:
            fire_cannon = False
            
        return  fire_cannon
    
    
class EnemySprite(FighterSprite):
    '''Class used for enemy fighters.'''
    
    piloting_cone_sine = 0.05
    gunning_cone_sine = 0.1
    #screen,meta_data,sprite_name,*groups,**initial_values
    def __init__(self,screen,sprite_meta_data,laser_meta_data,laser_beams_group,player,*groups,**initial_values):
        
        FighterSprite.__init__(self,screen,sprite_meta_data,laser_meta_data,laser_beams_group,*groups,**initial_values)
        
        # attach group containing player sprite
        self.player = player
        
        
    def use_radar(self):
        '''Util method used by piloting and gunning methods. Yields player position
        relative to the enemy sprite by calculating the projection of the 
        enemy -> player connecting line on the vector orthogonal to the enemy's
        current direction of flight. This allows the enemy to see whether to turn
        left or right to get closer to the player.'''
        
        # get own directional unit vector
        angle_degrees = self._angle * pi / 180
        direction = np.array([cos(angle_degrees ),-sin(angle_degrees )])
        clockwise_ortnorm = np.array([direction[1],-direction[0]])
        
        # get clockwise rotated orthogonal to unit vector pointing towards player position
        rel_player_position = (self.player._center - self._center)
        rel_player_position /= np.linalg.norm(rel_player_position)
        
        # turn towards player, whichever way is more aligned with current direction of movement
        projection_on_ortnorm = np.dot(clockwise_ortnorm,rel_player_position)
        
        return projection_on_ortnorm
    
    def get_pilot_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()

        # turn towards player, whichever way is more aligned with current direction of movement        
        if projection_on_ortnorm > self.__class__.piloting_cone_sine:
            # turn left
            d_angle = self._d_angle
        elif projection_on_ortnorm < -self.__class__.piloting_cone_sine:
            # turn right
            d_angle = - self._d_angle
        else:
            # continue straight on
            d_angle = 0
            
        d_speed = 0
        
        return d_angle, d_speed
        
    def get_gunner_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()
        
        # if player within 'cone of reasonable accuracy', shoot
        if - self.__class__.gunning_cone_sine < projection_on_ortnorm < self.__class__.gunning_cone_sine:
            # make decision to fire
            fire_cannon = True
        else:
            fire_cannon = False
        
        return fire_cannon

    
            
class LaserSprite(MaskedSprite):
    
    def __init__(self,
                 screen,
                 laser_meta_data,
                 time_left,
                 *groups,
                 angle=0,
                 speed=0,
                 center=0):
        
        MaskedSprite.__init__(self,
                              screen,
                              laser_meta_data,
                              *groups,
                              angle=angle,
                              speed=speed,
                              center=center)

        # set life time attribute
        self.time_left = time_left
    
    def update(self):
        '''Updates the sprite's position.'''
        
        # update timer
        self.time_left -= 1
        
        # self-destruct if timer has reached 0
        if not self.time_left:
            self.kill()
        
        # move the laser beam at constant speed
        self.move_ip(0)
