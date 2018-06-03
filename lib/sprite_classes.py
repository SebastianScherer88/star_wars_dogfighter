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
from animation_classes import BasicAnimationNew
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
        
        # set sprite up
        # set image and rect - these will be called by Group object methods; get mask
        self._image_index = 0 # always start with first image in original_images
        self.image = pg.transform.rotate(self._original_images[self._image_index],
                                         self._angle)
        
        # update object type attribute: mask
        self.mask = pg.mask.from_surface(self.image)
        
        # update object type attributes: positional rectangle
        self.rect = self.image.get_rect()
        self.rect.center = self._center
        
    def update_positional_attributes(self,
                                     d_angle=0,
                                     d_speed=0):
        '''Updates the sprites positional attributes '_angle' and '_speed'.
        Does not update the 'image','rect' or 'mask' attributes.'''
        
        # update angle argument
        self._angle += d_angle
        
        # update speed argument
        self._speed += d_speed
        
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
        
        # convert speed (pixel per second) into frame_speed (pixel per frame)
        frame_speed = self._speed / self._fps
        
        # compute velocity vector
        velocity = frame_speed * np.array([cos(radian_angle),
                                           -sin(radian_angle)]).reshape((1,2)) # in pygame coordinates, the y-axis has negative orientation
        
        return velocity.reshape(2)
    
    def get_pilot_commands(self):
        '''Calculates scalar floats d_angle and d_speed which can be 
        picked up by the self.update_positional_Attributes method called from within
        the update() method. For this base class, it returns trivial changes 0 for both
        arguments, but can be edited in more sophisticated classes to effectively
        implement player controls input or an AI pilot.'''
        
        return 0, 0
    
    def update(self):
        '''Updates the sprite's object type attributes 'image','rect' and 'mask' based on 
        updated numerical positional attributes'self._angle','self._speed' and self_center'.'''
        
        # get directional changes
        d_angle, d_speed = self.get_pilot_commands()
        
        # update numerical positional attributes
        self.update_positional_attributes(d_angle,
                                          d_speed)
        
        # update object type attributes: surface
        self.image = pg.transform.rotate(self._original_images[self._image_index],
                                         self._angle)

        # update object type attribute: mask
        self.mask = pg.mask.from_surface(self.image)
        
        # update object type attributes: positional rectangle
        self.rect = self.image.get_rect()
        self.rect.center = self._center
        
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
        self._time_of_last_shot = pg.time_get_ticks() - (1 / self._laser_rate_in_seconds) * 1000 # this allows to fire laser from the beginning
        
        # set attributes for explosion animation at death
        self._explosion_group = explosion_group
        self._explosion_sound - explosion_sound
        self._original_explosion_images = original_explosion_images
        self._explosion_seconds_per_image = explosion_seconds_per_image
        
        # set motion control attributes
        self._d_angle_degrees_per_frame = d_angle_degrees_per_second / self._fps
        self._d_speed_pixel_per_frame = d_speed_pixel_per_second / self._fps
        self._max_speed_pixel_per_frame = max_speed_pixel_per_second / self._fps
        
        
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
        cannon_down_time = (self._time_of_last_shot - pg.time.get_ticks()) / 1000
        
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
                           gun_muzzle_flash_position,
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
        
        fire = self.get_gunner_commands(self)
        
        if fire and self._is_cannon_ready():
            # fire the cannon
            self.fire()
            
        # draw muzzle flashes to ShipSprite's surface if needed
        if (pg.time.get_ticks() - self._time_of_last_shot) / 1000 < self.__class__._muzzle_flash_lifetime_in_seconds:
            self._draw_cannon_muzzle_flashes()
            
    def kill(self):
        '''Base class kill method plus moving explosion animation.'''
        
        # remove self from all groups
        self.kill()
        
        # create explosion animation
        BasicAnimationNew(self._fps,
                          self._screen,
                          self._original_explosion_images,
                          self._explosion_seconds_per_image,
                          self._explosion_group,
                          center = self._center,
                          angle = self._angle,
                          speed = self._speed)
        
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
                             *groups,
                             center = np.zeros(2),
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
        towards_player_vector = (self.player._center - self._center)
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
                                

class MaskedSprite(Sprite):
    
    def __init__(self,
                 screen,
                 sprite_meta_data,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.zeros(2)):
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
    
    def __init__(self,
                 screen,
                 sprite_meta_data,
                 laser_meta_data,
                 laser_beams_group,
                 laser_sound,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.zeros(2)):
        
        # call parent class __init__
        MaskedSprite.__init__(self,
                              screen,
                              sprite_meta_data,
                              *groups,
                              angle=angle,
                              speed=speed,
                              center=center)
        
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

        # attach laser soud
        self._laser_sound = laser_sound
        
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
            
            # spawn laser at gun tip
            LaserSprite(laser_screen,
                        self.laser_meta_data,
                        self._laser_sound,
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
    def __init__(self,
                 screen,
                 sprite_meta_data,
                 laser_meta_data,
                 laser_beams_group,
                 laser_sound,
                 player,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.zeros((1,1))):
        
        FighterSprite.__init__(self,
                               screen,
                               sprite_meta_data,
                               laser_meta_data,
                               laser_beams_group,
                               laser_sound,
                               *groups,
                               angle=angle,
                               speed=speed,
                               center=center)
        
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
                 laser_sound_object,
                 time_left,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.zeros(2)):
        
        MaskedSprite.__init__(self,
                              screen,
                              laser_meta_data,
                              *groups,
                              angle=angle,
                              speed=speed,
                              center=center)
        
        # load sound file specified in meta data and play
        #laser_sound = pg.mixer.Sound(file=laser_meta_data['sound_path']) # load wav file into sound object
        #laser_sound.play() # play sound object on any available channnel
        
        laser_sound_object.play()

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
