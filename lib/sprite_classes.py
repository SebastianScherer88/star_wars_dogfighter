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
from basic_sprite_classes import BasicSprite
from animation_classes import BasicAnimation, TrackingAnimation
from weapons_classes import LaserCannon
from math import cos, sin, pi
from pygame.sprite import Group
from random import randint

import pygame as pg
import numpy as np



class ShipSprite(BasicSprite):
    '''Base sprite class for both the player's and the enemy ship(s).'''
    
    _muzzle_flash_lifetime_in_seconds = 0.1
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 laser_cannon_offsets,
                 laser_fire_modes,
                 laser_group,
                 laser_sound,
                 original_laser_beam_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 original_muzzle_flash_images,
                 muzzle_flash_seconds_per_image,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 animation_group,
                 groups,
                 hostile_ships_group = None,
                 ship_id = None,
                 hit_points = 30,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 min_speed_pixel_per_second = 10,
                 is_transparent = True,
                 transparent_color = (255,255,255),
                 **trash_can):
    
        '''Arguments:
            
            fps: frames per second ratio of surrounding pygame
             screen: the main screen the game is displayed on (pygame Surface).
                    Needed to 'wrap' sprites around edges to produce 'donut topology'.
            original_images: list of surface objects that will be used to display the sprite.
                    By default, the first list element will be used.
            laser_cannon_offsets: array of relative pixel positions of sprite's gun muzzles w.r.t
                    sprite skin's center.
            laser_fire_modes: dictionary of meta data specifyinh the ship's possible fire modes.
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
            laser_rate_in_seconds: number of lasers that the ShipSprite can fire per second (i.e. rate of fire)
            explosion_group: pygame Group object. When ShipSprite is terminated, an explosion animation will be created
                    and added to this group.
            explosion_sound: pygame.mixer.Sound object. Will be played for the explosion animation
            original_explosion_images: list of surface objets that will be used to display the explosion animation
                    at time of ShipSprite's death.
            explosion_seconds_per_image: seconds_per_image value that will be passed to the 
                    explosion animation at time of ShipSprite's death
            groups: tuple of pygame Group objects. The sprite will add itself to each of these
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
                    is set to true. Default to (255,255,255), which corresponds to the color white.
            **trash_can: collects all unknown key word arguments provided to the initializer at call-time.
                    Allows for dictionary style argument plumbing further upstream.'''
                    
        # set sound toggle variable to default False
        self._sound = False
        
        # set ships id
        self._ship_id = ship_id
                    
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
        
        # set active state variable to communicate to tracking animations
        self._alive = True
        
        print("Ship image colorkey:", self.image.get_colorkey())
        
        # set laser fire meta data attributes            
        self._original_laser_fire_modes = laser_fire_modes
        self._laser_sound = laser_sound
        #self._laser_sound = pg.mixer.Sound(file=laser_sound)
        
        # intialize and attach laser weapons
        self._laser_cannons = []
        
        for laser_cannon_offset in laser_cannon_offsets * self._size_factor:
            # for each weapon offset in the ship skin's meta data, we create and 
            # attach a LaserCannon object
            self._laser_cannons.append(LaserCannon(ship_sprite=self,
                                                     cannon_offset=laser_cannon_offset,
                                                     cannon_fire_rate=laser_rate_in_seconds,
                                                     cannon_range_in_seconds=laser_range_in_seconds,
                                                     cannon_projectile_speed_in_seconds=laser_speed_in_seconds,
                                                     cannon_projectile_group=laser_group,
                                                     original_laser_beam_images=original_laser_beam_images,
                                                     original_muzzle_flash_images=original_muzzle_flash_images,
                                                     muzzle_flash_animation_spi=muzzle_flash_seconds_per_image))

        # attach hostile ships and current target group
        self._hostile_ships_group = hostile_ships_group
        self._current_target = Group() # this needs to be a group even though its just one sprite at a time
        
        # acquire target if possible
        self._acquire_target()
        
        # attach animations group to sprite
        self._animation_group = animation_group
        
        # set hit points attributes
        self._max_hit_points = hit_points
        self._hit_points = hit_points
        
        # set attributes for explosion animation at death
        self._explosion_sound = explosion_sound
        self._original_explosion_images = original_explosion_images
        self._explosion_seconds_per_image = explosion_seconds_per_image
        
        # set attributes for engine animation when moving
        self._engine_flame_offsets = engine_flame_offsets
        self._original_engine_flame_images = original_engine_flame_images
        self._engine_flame_seconds_per_image = engine_flame_seconds_per_image
        
        # set motion control attributes
        self._d_angle_degrees_per_frame = d_angle_degrees_per_second / self._fps
        self._d_speed_pixel_per_frame = d_speed_pixel_per_second / self._fps
        self._max_speed_pixel_per_frame = max_speed_pixel_per_second / self._fps
        self._min_speed_pixel_per_frame = min_speed_pixel_per_second / self._fps
        
        # set firing control attributes
        self._command_to_fire = False
        
        # set initial fire mode to coupled cannons, set cannon index to 0
        self._fire_mode_index = 1
        self._cannon_index = 0
        
        # create engine flame animation(s)
        self._engine_animations = []
        
        if self._speed:
            self._create_engine_animations()
            
    def _toggle_fire_mode(self):
        '''Util function that takes an integer and uses it to set one of the at least
        2 different laser fire modes ('single' or 'coupled').'''
                                     
        # switch to next fire mode
        self._fire_mode_index = (self._fire_mode_index + 1) % len(self._original_laser_fire_modes)
        
        # set cannon index back to zero to avoid out of bounds indices when downsampling fire mode
        self._cannon_index = 0  
        
    def _create_engine_animations(self):
        '''Util method to create engine animations.'''
        
        for engine_flame_offset in self._engine_flame_offsets:
            self._engine_animations.append(TrackingAnimation(self._fps,
                                                             self._screen,
                                                             self._original_engine_flame_images,
                                                             self._engine_flame_seconds_per_image,
                                                             self,
                                                             engine_flame_offset * self._size_factor,
                                                             [self._animation_group],
                                                             looping = True))
        
    def set_gunner_commands(self):
        '''Dummy placeholder method to set the command_to_fire attribute. Used 
        for AI controlled sprites only.'''
        
        return
    
    def _get_next_cannons(self):
        '''Util function that returns a list of laser cannons next in line to be fired.'''
        
        # get index set for cannons lined up to fir enext
        laser_cannon_index_set = self._original_laser_fire_modes[self._fire_mode_index][self._cannon_index]
        
        return [self._laser_cannons[i] for i in laser_cannon_index_set]
    
    def _pause_next_cannons(self):
        '''Util function that makes the set of cannons which are next in line
        to fire wait an appropriate amount of time to guarantee evenly spaced fire.'''
        
        # get number of salves per cycle for current firing mode
        n_salves = len(self._original_laser_fire_modes[self._fire_mode_index])
        
        for next_cannon in self._get_next_cannons():
            now = pg.time.get_ticks()
            mil_seconds_per_shot = 1000 / next_cannon._rate_of_fire
            next_cannon._time_of_last_shot = now - (n_salves - 1) / n_salves * mil_seconds_per_shot

    def fire(self):
        '''Creates a MissileSprite objects at SpriteShip's specified locations
        of gun muzzles.'''
        
        
        # play laser sound if sound is on
        if self._sound:
            self._laser_sound.play()
        
        # fire cannons
        [laser_cannon.fire() for laser_cannon in self._get_next_cannons()]
        
        # update cannon index within current fire mode
        self._cannon_index = (self._cannon_index + 1) % len(self._original_laser_fire_modes[self._fire_mode_index])
        
        # update cannons next in line so they wait as approrpiate
        self._pause_next_cannons()
            
    def _control_speed(self):
        '''Util function that gets called from within set_pilot_commands for all
        ShipSprite (based) classes to enforce ship's min & max speed limits.'''
                   
        # if told to speed up make sure not to exceed max speed
        self._speed = min(self._speed,
                          self._max_speed_pixel_per_frame)
            
        # if told to slow down, make sure not to fall below min speed
        self._speed = max(self._speed,
                          self._min_speed_pixel_per_frame)
        
    def _acquire_target(self):
        '''Util function that assigns adds a ShipSprite from the hostile_ships
        group to the current_target group, if feasible. Dummy method at ShipSprite
        level, to be used for AIShipSprite class.'''
        
    def update(self):
        '''Base class update plus additional ShipSprite specific updates.'''
        
        # if no target has been aquired, get it
        if not self._current_target:
            self._acquire_target()
        
        # call base class update method
        BasicSprite.update(self)
        
        # get command to fire from custom method
        self.set_gunner_commands()
        
        # if command to fire was given, check if cannons are ready; if so, fire
        if self._command_to_fire and np.mean([cannon.is_ready() for cannon in self._get_next_cannons()]):
            # fire the cannon(s)
            self.fire()
            
    def kill(self):
        '''Base class kill method plus moving explosion animation.'''
        
        # play sound of explosion if sound on
        if self._sound:
            self._explosion_sound.play()
        
        # remove self from all groups
        BasicSprite.kill(self)
        
        # update live state variable
        self._alive = False
        
        # create explosion animation
        BasicAnimation(self._fps,
                      self._screen,
                      self._original_explosion_images,
                      self._explosion_seconds_per_image,
                      [self._animation_group],
                      center = self._center,
                      angle = self._angle,
                      speed = self._speed * self._fps) # animation expects pixel/second speed unit
        
class AIShipSprite(ShipSprite):
    '''Based on ShipSprite class. Represents an enemy ship during game.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 laser_cannon_offsets,
                 laser_fire_modes,
                 laser_group,
                 laser_sound,
                 original_laser_beam_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 original_muzzle_flash_images,
                 muzzle_flash_seconds_per_image,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 animation_group,
                 piloting_cone_sine,
                 gunning_cone_sine,
                 groups,
                 hostile_ships_group,
                 ship_id = None,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 is_transparent = True,
                 transparent_color = (255,255,255),
                 **trash_can):
    
        '''Arguments: All as in base class's (ShipSprite) __init__ method, except
        for 
            player_ship_sprite: PlayerShipSprite object representing the player during game.
                                Used for EnemyShipSprite's piloting and gunning methods.
            piloting_cone_sine: Sine of half of cone representing the enemy pilot's field of sight.
                If pilot can not see the PlayerShipSprite, he will turn to get him back into
                view.
            gunning_cone_sine: Sine of half of the cone representing the enemy gunner's target sight.
                If PlayerShipSprite is within this cone, gunner will attempt to fire cannon.
            **trash_can: collects all unknown key word arguments provided to the initializer at call-time.
                    Allows for dictionary style argument plumbing further upstream.'''
                                
        ShipSprite.__init__(self,
                            fps,
                            screen,
                            original_images,
                            laser_cannon_offsets,
                            laser_fire_modes,
                            laser_group,
                            laser_sound,
                            original_laser_beam_images,
                            laser_range_in_seconds,
                            laser_speed_in_seconds,
                            laser_rate_in_seconds,
                            original_muzzle_flash_images,
                            muzzle_flash_seconds_per_image,
                            explosion_sound,
                            original_explosion_images,
                            explosion_seconds_per_image,
                            engine_flame_offsets,
                            original_engine_flame_images,
                            engine_flame_seconds_per_image,
                            animation_group,
                             groups,
                             hostile_ships_group = hostile_ships_group,
                             ship_id = ship_id,
                             center = center,
                             angle = angle,
                             speed = speed,
                             d_angle_degrees_per_second = d_angle_degrees_per_second,
                             d_speed_pixel_per_second = d_speed_pixel_per_second,
                             max_speed_pixel_per_second = max_speed_pixel_per_second,
                             is_transparent = is_transparent,
                             transparent_color = transparent_color)
        
        # attach the AI cone sines
        self._piloting_cone_sine = piloting_cone_sine
        self._gunning_cone_sine = gunning_cone_sine
        
    def _acquire_target(self):
        '''Util function to select and add to current_target group.'''
                
        # if there are hostile ships, randomly select one
        if self._hostile_ships_group:
            target_index = randint(0,len(self._hostile_ships_group)-1)
            self._current_target.add(self._hostile_ships_group.sprites()[target_index])
        
    def use_radar(self):
        '''Util method used by piloting and gunning methods. Yields current target's 
        position relative to the enemy sprite by calculating the projection of the 
        enemy -> player connecting line on the vector orthogonal to the enemy's
        current direction of flight. This allows the enemy to see whether to turn
        left or right to get closer to the current target. Only called when 
        a current target is selected.'''
        
        # get hostile ship sprite
        current_target = self._current_target.sprites()[0]
        
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
        towards_target_vector = (current_target._center - self._center)
        unit_towards_target_vector = towards_target_vector / np.linalg.norm(towards_target_vector)
        
        # turn towards player, whichever way is more aligned with current direction of movement
        projection_on_ortnorm = np.dot(clockwise_ortnorm_direction,
                                       unit_towards_target_vector)
        
        return projection_on_ortnorm
    
    def set_pilot_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # only make piloting decisions if there is a current target
        if not self._current_target:
            return
        
        # have a look at the radar to see where target is
        projection_on_ortnorm = self.use_radar()

        # turn towards player, whichever way is more aligned with current direction of movement        
        if projection_on_ortnorm > self._piloting_cone_sine:
            # turn left
            self._d_angle = self._d_angle_degrees_per_frame
        elif projection_on_ortnorm < -self._piloting_cone_sine:
            # turn right
            self._d_angle = - self._d_angle_degrees_per_frame
        else:
            # continue straight on
            self._d_angle = 0
        
        
    def set_gunner_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
                # only make piloting decisions if there is a current target
        if not self._current_target:
            return
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()
        
        # if player within 'cone of reasonable accuracy', attempt to fire cannon.
        # Otherwise, dont attempt to fire cannon
        self._command_to_fire = -self._gunning_cone_sine < projection_on_ortnorm < self._gunning_cone_sine
        
class ShipBio(Sprite):
    
    '''Class used to display the ships' stats to the main game screen inside 
    the appropriate cockpit frame.'''
    
    def __init__(self,
                 pilot_images,
                 reference_ship,
                 side,
                 groups,
                 mode='text',
                 font = 'freesansbold.ttf',
                 size = 15,
                 center = np.zeros(2)):
        
        # add to group(s)
        Sprite.__init__(self,
                        *groups)
        
        # attch display mode
        self.display_mode = mode
        
        if side == 'hostile':
            self.frame_color = (255,0,0) # red
            self.opp_frame_color = (0,255,0) # green
        elif side == 'ally':
            self.frame_color = (0,255,0)# green
            self.opp_frame_color = (255,0,0) # red
        else:
            self.frame_color = (255,255,0) # yellow
            self.opp_frame_color = (255,0,0) # red
            
        self.base_text_color = (0,200,200) # light blue
        self.base_display_color = (0,70,70) # dark blue
        
        # attach font
        self._font = pg.font.Font(font,size)
        
        # attach original pilot image
        self._original_pilot_image = pilot_images
        
        # attach reference ship
        self._source_ship = reference_ship
        
        # attach max hp pf reference ship
        self._source_ship_max_hp = reference_ship._hit_points
        
        # attach ship id of reference ship
        self._source_ship_id = reference_ship._ship_id
        
        # initialize stats reference storage for comparison
        self._previous_stats = self._get_current_stats()
        
        # assemble the "ID card" for given ship using pilot image and ship
        ship_bio_image = self._get_ship_bio_image()
        
        # attach current id card to sprite
        self.image = ship_bio_image
        
        # position id card on main screen; this position will not change
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    def _get_current_stats(self):
        '''Util function that gets up to date values of stats to be displayed.'''
        
        currently_alive = self._source_ship._alive # currently alive? (boolean)
        current_hps = self._source_ship._hit_points # curent hps (integer)
        current_target_id_list = [ship._ship_id for ship in self._source_ship._current_target.sprites()] # list containing target's id string; may be empty
        current_target_image = self._source_ship.image
        
        if not current_target_id_list:
            current_target_id = ""
        else:
            current_target_id = current_target_id_list[0]
        
        return currently_alive, current_hps, current_target_id, current_target_image
    
    def _have_stats_changed(self):
        '''Util function that checks previous ship stats against current ship stats
        to check if image update is necessary. Used to reduce the times a new ship id card
        is rendered.'''
        
        return self._previous_stats != self._get_current_stats()
    
    def _render_text(self,
                     text,
                     text_color=(0,200,200)):
        '''Util function that renders a text message to a pygame surface and
        returns the surface.'''
        
        # text surface is transparent by default
        text_surface = self._font.render(text,True,text_color)
        
        return text_surface
        
    def _get_ship_bio_image(self):
        '''Util function that assembles the pygame surface visually representing
        the current ship status on the cockpit frame.'''
        
        # get shortcuts to needed attributes
        pilot_images = self._original_pilot_image
        
        # get the ship's stats
        ship_is_alive, ship_hp, ships_target_id, ship_image = self._get_current_stats()
        
        ship_max_hp = self._source_ship_max_hp
        ship_id = self._source_ship_id
        
        # get blank id card canvas surface with a coloured frame depending on side attribute
        id_template = pg.Surface((280,120))
        id_template.fill((0,70,70)) # dark blue on the inside
        frame_thickness = 5
        frame_rect = pg.Rect(0,0,280, 120)# coloured frame positional rectangle
        pg.draw.rect(id_template, self.frame_color, frame_rect, frame_thickness)
        
        # blit appropriate pilot image to id_template
        if ship_is_alive:
            id_template.blit(pilot_images[0],(10,10)) # first image in sequence shows alive pilot
        elif not ship_is_alive:
            id_template.blit(pilot_images[1],(10,10)) # second image in sequence shows dead pilot
            
        # get current hp color:
        if 0.2 <= (ship_hp / ship_max_hp) < 0.5:
            hp_color = (255,255,0) # yellow
        elif ship_hp / ship_max_hp < 0.2:
            hp_color = (255,0,0) # RED
        else:
            hp_color = (0,255,0) # green
            
        # blit stats
        if self.display_mode == 'text':
            for (top_left_y, text,text_color) in zip([10,35,50,75,90],
                                          [ship_id,"Current target", ships_target_id, "Status report", str(ship_hp) + " / " + str(ship_max_hp)],
                                          [self.frame_color,self.base_text_color,self.opp_frame_color,self.base_text_color,hp_color]):          
                # render text message
                #stat_surface = self._render_text(text)
                stat_surface = self._font.render(text,True,text_color)
                
                # get top left position of text surface to be blit
                top_left = (120,top_left_y)
                
                # blit stat surface
                id_template.blit(stat_surface,top_left)
        elif self.display_mode == 'graphic':
            ship_image_w, ship_image_h = ship_image.get_rect().size
            left_buffer, top_buffer = 160 - int(ship_image_w/2), 40 - int(ship_image_h/2)
            id_template.blit(ship_image, (left_buffer, top_buffer))
            
        return id_template
            
    def update(self):
        '''Updates the sprite's image attribute based on previous/current ship
        stats.'''
        
        # only render an updated surface if really necessary
        if self._have_stats_changed():
            self.image = self._get_ship_bio_image()