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

from basic_sprite_class import BasicSprite
from animation_classes import BasicAnimation, TrackingAnimation
from math import cos, sin, pi

import pygame as pg
import numpy as np

        
class MissileSprite(BasicSprite):
    '''Class used for projectiles fired by player or enemy sprites.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 lifetime_in_seconds,
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
            lifetime: lifetime pf sprite (in seconds).
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
                    
        # initialize and add to groups if sensible
        BasicSprite.__init__(self,
                             fps,
                             screen,
                             original_images,
                             *groups,
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
            

class ShipSprite(BasicSprite):
    '''Base sprite class for both the player's and the enemy ship(s).'''
    
    _muzzle_flash_lifetime_in_seconds = 0.1
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 original_laser_cannon_positions,
                 laser_group,
                 laser_sound,
                 laser_original_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 explosion_group,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 engine_flame_group,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 is_transparent = True,
                 transparent_color = (255,255,255)):
    
        '''Arguments:
            
            fps: frames per second ratio of surrounding pygame
             screen: the main screen the game is displayed on (pygame Surface).
                    Needed to 'wrap' sprites around edges to produce 'donut topology'.
            original_images: list of surface objects that will be used to display the sprite.
                    By default, the first list element will be used.
            original_laser_cannon_positions: array of relative pixel positions of sprite's gun muzzles w.r.t
                    sprite skin's center.
            laser_group: pygame Group object. Any laser created by the ShipSprite's firing method
                    will be added to this group to help track laser fire collisions.
            laser_sound: pygame.mixer.Sound object. Will be played by the ShipSprite's firing method.
            laser_original_images: The original_images sequence that will be passed to the MissileSprite
                    object created by the ShipSprite's firing method. A list of pygame surfaces.
            laser_range_in_seconds: effectively the laser weapon range of the ship sprite. When the 
                    ShipSprite's firing method creates a MissileSprite, this value will be passed to it
                    as its lifetime_in_seconds argument.
            laser_speed_in_seconds: this value will be added to personal _speed attribute value at time
                    of firing cannon. The sum of those values will be passed to the MissileSprite as initial
                    _speed value.
            laser_rate_in_seconds: number of lasers that the ShipSprite can fire per seconds (i.e. rate of fire)
            explosion_group: pygame Group object. When ShipSprite is terminated, an explosion animation will be created
                    and added to this group.
            explosion_sound: pygame.mixer.Sound object. Will be played for the explosion animation
            original_explosion_images: list of surface objets that will be used to display the explosion animation
                    at time of ShipSprite's death.
            explosion_seconds_per_image: seconds_per_image value that will be passed to the 
                    explosion animation at time of ShipSprite's death
            *groups: tuple of pygame Group objects. The sprite will add itself to each of these
                    when initialized.
            center: initial position of center of sprite's rectangle (numpy float-type array of shape (2,)).
                    Sets the sprite's initial position on the 'screen' surface.
            angle: initial orientation of sprite in degrees. Angle is taken counter-clockwise, with
                    an angle of zero meaning no rotation of the original surface.
            speed: initial speed of sprite (pixels per second). scaler of float type.
                    Default is 0.
            d_angle_degrees_per_second: Rate of change for ShipSprite's angle (in degrees, per second).
            d_speed_pixel_per_second: Rate of change for ShipSprite's speed (in pixels/second, per second).
            max_speed_pixel_per_second: Maximum speed for ShipSprite (in pixels per second).
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
                             *groups,
                             center=center,
                             angle=angle,
                             speed=speed,
                             is_transparent=is_transparent,
                             transparent_color=transparent_color)
        
        # set attributes for lasers
        self._original_laser_cannon_positions = original_laser_cannon_positions
        self._laser_group = laser_group
        self._laser_sound = laser_sound
        self._laser_original_images = laser_original_images
        self._laser_range_in_seconds = laser_range_in_seconds
        self._laser_speed_in_seconds = laser_speed_in_seconds
        self._laser_rate_in_seconds = laser_rate_in_seconds
        self._time_of_last_shot = pg.time.get_ticks() - (1 / self._laser_rate_in_seconds) * 1000 # this allows to fire laser from the beginning
        
        # set attributes for explosion animation at death
        self._explosion_group = explosion_group
        self._explosion_sound = explosion_sound
        self._original_explosion_images = original_explosion_images
        self._explosion_seconds_per_image = explosion_seconds_per_image
        
        # set motion control attributes
        self._d_angle_degrees_per_frame = d_angle_degrees_per_second / self._fps
        self._d_speed_pixel_per_frame = d_speed_pixel_per_second / self._fps
        self._max_speed_pixel_per_frame = max_speed_pixel_per_second / self._fps
        
        # create engine flame animation(s)
        for engine_flame_offset in engine_flame_offsets:
            TrackingAnimation(self._fps,
                             self._screen,
                             original_engine_flame_images,
                             engine_flame_seconds_per_image,
                             self,
                             engine_flame_offset,
                             engine_flame_group,
                             looping = True)
        
    def get_gunner_commands(self):
        '''Returns True if ShipSprite should fire, or False otherwise.
        For the ShipSprite base class trivially always returns False.
        For more sophisticated classes, this method will handle player input
        or an AI gunner and return a non-trivial boolean.'''
        
        return False
    
    def _is_cannon_ready(self):
        '''Checks if cannon is ready to fire, based on _laser_rate_in_seconds
        attribute.'''
        
        # get time between now and last shot in seconds
        cannon_down_time = (pg.time.get_ticks() - self._time_of_last_shot) / 1000
                           
        #print('cannon down time:',cannon_down_time)
        
        # make sure enough time has passed since last shot
        if cannon_down_time > 1 / self._laser_rate_in_seconds:
            # cannon is ready
            return True
        elif cannon_down_time <= 1 / self._laser_rate_in_seconds:
            # cannon is not ready
            return False
            
    def _get_cannon_muzzle_positions(self,
                                     absolute_positions=True):
        '''Calculates the current pixel positions of the sprite's
        gun muzzle positions w.r.t main screen's coordinate system.
        If flag is set to False, calculates them relative to ShipSprite's 
        surface's coordinate system.'''
        
        # convert ship's current angle to radian
        radian_angle = self._angle * pi / 180
        
        # get rotation matrix for radian angle
        rotation_matrix = np.array([[cos(radian_angle), sin(radian_angle)],
                                   [- sin(radian_angle), cos(radian_angle)]])
        
        # rotate relative gun tip positions around center of ShipSprite's surface
        rotated_gun_muzzle_positions = np.dot(rotation_matrix,
                                              self._original_laser_cannon_positions.T).T
        
        # if absolute_positions flag is not raised, return coordinates w.r.t to
        # ShipSprite's surface's coordinate origin
        if not absolute_positions:
            gun_muzzle_positions = np.array(self.image.get_size()) / 2 + rotated_gun_muzzle_positions
        # if absolute_position's flag is raised, return coordinates w.r.t to the
        # main game's surface's coordinate origin
        elif absolute_positions:
            gun_muzzle_positions = self._center + rotated_gun_muzzle_positions
        
        return gun_muzzle_positions
    
    def _draw_cannon_muzzle_flashes(self):
        '''Draws the cannon muzzle flashes from firing lasers to the ShipSprite's
        surface as red dots, at the specified gun muzzle positions.'''
        
        # get positions of gun muzzle flashes
        gun_muzzle_flash_positions = self._get_cannon_muzzle_positions(absolute_positions=False)
        
        # draw one flash as a red dot to SpriteShip surface for each gun
        for gun_muzzle_flash_position in gun_muzzle_flash_positions:
            pg.draw.circle(self.image,
                           (255,0,0),
                           gun_muzzle_flash_position.astype('int'),
                           2)
        
    
    def fire(self):
        '''Creates a MissileSprite objects at SpriteShip's specified locations
        of gun muzzles.'''
        
        # get locations of gun muzzles
        gun_muzzle_positions = self._get_cannon_muzzle_positions()
        
        # play laser sound
        self._laser_sound.play()
        
        # for each gun, create a laser at specified location
        for gun_muzzle_position in gun_muzzle_positions:
            MissileSprite(self._fps,
                 self._screen,
                 self._laser_original_images,
                 self._laser_range_in_seconds,
                 self._laser_group,
                 center = gun_muzzle_position,
                 angle = self._angle,
                 speed = self._speed * self._fps + self._laser_speed_in_seconds)
            
        # (re)set last_shot_fired attribute
        self._time_of_last_shot = pg.time.get_ticks()
            
            
    def update(self):
        '''Base class update plus additional ShipSprite specific updates.'''
        
        # call base class update method
        BasicSprite.update(self)
        
        fire = self.get_gunner_commands()
        
        #print('cannon ready:',self._is_cannon_ready())
        
        if fire and self._is_cannon_ready():
            # fire the cannon
            self.fire()
            
        # draw muzzle flashes to ShipSprite's surface if needed
        if (pg.time.get_ticks() - self._time_of_last_shot) / 1000 < self.__class__._muzzle_flash_lifetime_in_seconds:
            self._draw_cannon_muzzle_flashes()
            
    def kill(self):
        '''Base class kill method plus moving explosion animation.'''
        
        # play sound of explosion
        self._explosion_sound.play()
        
        # remove self from all groups
        BasicSprite.kill(self)
        
        # create explosion animation
        BasicAnimation(self._fps,
                          self._screen,
                          self._original_explosion_images,
                          self._explosion_seconds_per_image,
                          self._explosion_group,
                          center = self._center,
                          angle = self._angle,
                          speed = self._speed * self._fps) # animation expects pixel/second speed unit
        
class PlayerShipSprite(ShipSprite):
    '''Class representing the player's sprite. Based on general ShipSprite class.
    
    For a description of the arguments of the PlayerShipSprite's __init__ method,
    please see the documentation of the base class (ShipSprite).'''
    
    
    def get_pilot_commands(self):
        '''Handles directional player controls, i. e. steering and accelerating.
        Returns a tuple of scalar floats (d_angle,d_speed), giving the change in
        degrees (counter-clockwise) per frame and the change in speed in pixels/frame^2,
        respectively.'''
        
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
            
        # get angle differential
        if pressed_keys[pg.K_LEFT] and not pressed_keys[pg.K_RIGHT]:
            # turn left
            d_angle = self._d_angle_degrees_per_frame
        elif pressed_keys[pg.K_RIGHT] and not pressed_keys[pg.K_LEFT]:
            # turn right            
            d_angle = -self._d_angle_degrees_per_frame
        else:
            # dont turn            
            d_angle = 0
            
        # get speed differential
        if pressed_keys[pg.K_UP] and not pressed_keys[pg.K_DOWN]:
            # dont accelerate above sprite's max speed
            d_speed = min(self._d_speed_pixel_per_frame,
                          self._max_speed_pixel_per_frame - self._speed)
        elif pressed_keys[pg.K_DOWN] and not pressed_keys[pg.K_UP]:
            # dont decelarate to going backwards
            d_speed = -min(self._d_speed_pixel_per_frame,
                           self._speed)
        else:
            # dont change speed
            d_speed = 0
            
        return d_angle, d_speed
    
    def get_gunner_commands(self):
        '''Handles shooting player controls, i.e. firing lasers.
        Returns True if player has the space bar pressed, and False
        otherwise'''
        
        #print(pg.key.get_pressed()[pg.K_SPACE])
        
        # space bar is pressed, fire command is given
        return pg.key.get_pressed()[pg.K_SPACE]
        
class EnemyShipSprite(ShipSprite):
    '''Based on ShipSprite class. Represents an enemy ship during game.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 original_laser_cannon_positions,
                 laser_group,
                 laser_sound,
                 laser_original_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 explosion_group,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 engine_flame_group,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 player_ship_sprite,
                 piloting_cone_sine,
                 gunning_cone_sine,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 is_transparent = True,
                 transparent_color = (255,255,255)):
    
        '''Arguments: All as in base class's (ShipSprite) __init__ method, except
        for 
            player_ship_sprite: PlayerShipSprite object representing the player during game.
                                Used for EnemyShipSprite's piloting and gunning methods.
            piloting_cone_sine: Sine of half of cone representing the enemy pilot's field of sight.
                If pilot can not see the PlayerShipSprite, he will turn to get him back into
                view.
            gunning_cone_sine: Sine of half of the cone representing the enemy gunner's target sight.
                If PlayerShipSprite is within this cone, gunner will attempt to fire cannon.'''
                                
        ShipSprite.__init__(self,
                            fps,
                             screen,
                             original_images,
                             original_laser_cannon_positions,
                             laser_group,
                             laser_sound,
                             laser_original_images,
                             laser_range_in_seconds,
                             laser_speed_in_seconds,
                             laser_rate_in_seconds,
                             explosion_group,
                             explosion_sound,
                             original_explosion_images,
                             explosion_seconds_per_image,
                             engine_flame_offsets,
                             engine_flame_group,
                             original_engine_flame_images,
                             engine_flame_seconds_per_image,
                             *groups,
                             center = center,
                             angle = angle,
                             speed = speed,
                             d_angle_degrees_per_second = d_angle_degrees_per_second,
                             d_speed_pixel_per_second = d_speed_pixel_per_second,
                             max_speed_pixel_per_second = max_speed_pixel_per_second,
                             is_transparent = is_transparent,
                             transparent_color = transparent_color)
        
        # attach the player's sprite object
        self._player_sprite = player_ship_sprite
        
        # attach the AI cone sines
        self._piloting_cone_sine = piloting_cone_sine
        self._gunning_cone_sine = gunning_cone_sine
        
    def use_radar(self):
        '''Util method used by piloting and gunning methods. Yields player position
        relative to the enemy sprite by calculating the projection of the 
        enemy -> player connecting line on the vector orthogonal to the enemy's
        current direction of flight. This allows the enemy to see whether to turn
        left or right to get closer to the player.'''
        
        # get own directional unit vector
        # convert angle to radian
        angle_radian = self._angle * pi / 180
        
        # get unit directional vector
        unit_direction = np.array([cos(angle_radian),
                              -sin(angle_radian)])
    
        # get clockwise oriented orthonormal to unit directional vector
        clockwise_ortnorm_direction = np.array([unit_direction[1],
                                                -unit_direction[0]])
        
        # get clockwise rotated orthogonal to unit vector pointing towards player position
        towards_player_vector = (self._player_sprite._center - self._center)
        unit_towards_player_vector = towards_player_vector / np.linalg.norm(towards_player_vector)
        
        # turn towards player, whichever way is more aligned with current direction of movement
        projection_on_ortnorm = np.dot(clockwise_ortnorm_direction,
                                       unit_towards_player_vector)
        
        return projection_on_ortnorm
    
    def get_pilot_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()

        # turn towards player, whichever way is more aligned with current direction of movement        
        if projection_on_ortnorm > self._piloting_cone_sine:
            # turn left
            d_angle = self._d_angle_degrees_per_frame
        elif projection_on_ortnorm < -self._piloting_cone_sine:
            # turn right
            d_angle = - self._d_angle_degrees_per_frame
        else:
            # continue straight on
            d_angle = 0
            
        # currently no logic to control AI acceleration
        d_speed = 0
        
        return d_angle, d_speed
        
    def get_gunner_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()
        
        # if player within 'cone of reasonable accuracy', attempt to fire cannon.
        # Otherwise, dont attempt to fire cannon
        return -self._gunning_cone_sine < projection_on_ortnorm < self._gunning_cone_sine