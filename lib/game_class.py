# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:09:47 2018

@author: Atreju Maischberger
"""

# demo gam states here
import sys
import os
import yaml

import pygame as pg
import numpy as np

from pygame.sprite import Group, collide_mask, groupcollide
from sprite_classes import ShipSprite, AIShipSprite

class Game(object):
    
    def __init__(self,
                 screen_width=1500,
                 screen_height=700,
                 fps=60,
                 background_image = None,
                enemy_down_time_in_seconds = 2):
        '''Initializes the game object and also the game'''
        
        # initialize pygame (handles pretty much eveything)
        pg.init()
        
        # create clock    
        self.clock = pg.time.Clock()
        
        self.background_image = pg.image.load('./graphics/star_wars_background_24bit.bmp')
        self.fps = fps
        self.enemy_down_time_in_seconds = enemy_down_time_in_seconds
        
        # initialize main screen
        size = screen_width, screen_height # set screen size
        self.screen = pg.display.set_mode(size)
        
        # load meta data
        with open('./meta/sprite_skins_meta_data.yaml','r') as skins_meta_file:
            skins_meta_data = yaml.load(skins_meta_file)
        
        with open('./meta/animations_meta_data.yaml','r') as animations_meta_file:
            animations_meta_data = yaml.load(animations_meta_file)
        
        
        # set player and enemy ship and laser types
        allied_ship, allied_laser = 'xwing', 'red'
        hostile_ship, hostile_laser = 'tiefighter', 'green'
        
        # set game attributes from meta data for player
        
        # skin specific
        self.allied_images = [pg.image.load(image_path) for image_path in skins_meta_data[allied_ship]['image_paths']]
        self.allied_gun_offsets = np.array(skins_meta_data[allied_ship]['gun_offsets']).astype('float')
        self.allied_engine_offsets = np.array(skins_meta_data[allied_ship]['engine_offsets']).astype('float')
        self.allied_fire_modes = skins_meta_data[allied_ship]['fire_modes']
        
        # laser specific
        self.allied_laser_images = [pg.image.load(image_path) for image_path in skins_meta_data[allied_laser]['image_paths']]
        self.allied_laser_sound = pg.mixer.Sound(animations_meta_data[allied_laser]['sound'])
        self.allied_muzzle_images = [pg.image.load(image_path) for image_path in animations_meta_data[allied_laser]['image_paths']]
        self.allied_muzzle_spi = animations_meta_data[allied_laser]['spi']
        
        
        # set game attributes from meta data for enemies
        
        # behavioural
        self.piloting_cone_sine = 0.1
        self.gunning_cone_sine = 0.1
        
        # skin specific
        self.hostile_images = [pg.image.load(image_path) for image_path in skins_meta_data[hostile_ship]['image_paths']]
        self.hostile_gun_offsets = np.array(skins_meta_data[hostile_ship]['gun_offsets']).astype('float')
        self.hostile_engine_offsets = np.array(skins_meta_data[hostile_ship]['engine_offsets']).astype('float')
        self.hostile_fire_modes = skins_meta_data[hostile_ship]['fire_modes']
        
        # laser specific
        self.hostile_laser_images = [pg.image.load(image_path) for image_path in skins_meta_data[hostile_laser]['image_paths']]
        self.hostile_laser_sound = pg.mixer.Sound(animations_meta_data[hostile_laser]['sound'])
        self.hostile_muzzle_images = [pg.image.load(image_path) for image_path in animations_meta_data[hostile_laser]['image_paths']]
        self.hostile_muzzle_spi = animations_meta_data[hostile_laser]['spi']
        
        # load universal game animation attributes from meta data
        
        # explosion
        self.explosion_images = [pg.image.load(image_path) for image_path in animations_meta_data['explosion']['image_paths']]
        self.explosion_sound = pg.mixer.Sound(animations_meta_data['explosion']['sound'])
        self.explosion_spi = animations_meta_data['explosion']['spi']
        
        # engine flame
        self.engine_images = [pg.image.load(image_path) for image_path in animations_meta_data['engine']['image_paths']]
        self.engine_spi = animations_meta_data['engine']['spi']
        
        # initialize empty sprite groups
        self.all_ships = Group()
        
        # player's groups
        self.allied_ships = Group()
        self.allied_laser_beams = Group()
        
        # enemy groups
        self.hostile_ships = Group()
        self.hostile_laser_beams = Group()
        
        # animation group
        self.animations = Group()        
        
        # create player sprite and add to relevant groups / provide with relevant groups
        player = self.spawn_player(center=np.array([1400,350]),
                                   angle=180,
                                   speed=250,
                                   d_angle_degrees_per_second = 150,
                                   max_speed_pixel_per_second=360)
        
        # create two wingmen
        self.spawn_ai_squadron('allied',
                               centers=[np.array([1400,100]),
                                        np.array([1400,700])],
                                angles=[0,
                                        0],
                                speeds=[300,
                                        300],
                                d_angle_degrees_per_seconds = [150,
                                                               150],
                                max_speed_pixel_per_seconds=[300,
                                                             300])
        
        # create three enemies
        self.spawn_ai_squadron('hostile',
                               centers=[np.array([50,100]),
                                        np.array([350,100]),
                                        np.array([50,700])],
                                angles=[180,
                                        180,
                                        180],
                                speeds=[300,
                                        300,
                                        300],
                                d_angle_degrees_per_seconds = [150,
                                                               150,
                                                               150],
                                max_speed_pixel_per_seconds=[300,
                                                             300,
                                                             300])
                                        
                        
        # initialize enemy down time so that 2 enemies are spawned at beginning of game
        hostile_down = False
        ally_down = False
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    
                    # quit pygame
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    
                    # control player fire mode
                    if event.key == pg.K_f:
                        player._toggle_fire_mode()
                        
                    # control player fire commands
                    if event.key == pg.K_SPACE:
                        player._command_to_fire = True
                        
                    # control player acceleration
                    if event.key == pg.K_UP:
                        player._d_speed += player._d_speed_pixel_per_frame
                    if event.key == pg.K_DOWN:
                        player._d_speed -= player._d_speed_pixel_per_frame
                        
                    # control player steering
                    if event.key == pg.K_RIGHT:
                        player._d_angle -= player._d_angle_degrees_per_frame
                    if event.key == pg.K_LEFT:
                        player._d_angle += player._d_angle_degrees_per_frame
                        
                elif event.type == pg.KEYUP:
                    
                    # control player fire commands
                    if event.key == pg.K_SPACE:
                        player._command_to_fire = False
                    
                    # control player acceleration
                    if event.key == pg.K_UP:
                        player._d_speed -= player._d_speed_pixel_per_frame
                    if event.key == pg.K_DOWN:
                        player._d_speed += player._d_speed_pixel_per_frame
                        
                    # control player steering
                    if event.key == pg.K_RIGHT:
                        player._d_angle += player._d_angle_degrees_per_frame
                    if event.key == pg.K_LEFT:
                        player._d_angle -= player._d_angle_degrees_per_frame
                        
            # spawn enemies if needed
            if hostile_down:
                # create first two enemy sprites and add to relevant groups / provide with relevant groups
                self.spawn_hostile(center=np.array([50,350]),
                         speed=300,
                         d_angle_degrees_per_second = 150,
                         max_speed_pixel_per_second=300)# enemy #1

                
            if ally_down:
                # reanimate player
                self.spawn_ally(center=np.array([1400,350]),
                                speed=300,
                                angle=180,
                                d_angle_degrees_per_second = 150,
                                max_speed_pixel_per_second=300)
                
            # update game state
            self.update_game_state()
            
            # draw update game state to screen
            self.draw_game_state()
            
            # check and handle collisions
            hostile_down, ally_down = self.handle_collisions()
                        
            # control pace
            self.clock.tick(fps)
            
    def update_game_state(self):
        '''Updates the game state by updating all the game's sprite groups.'''
        
        self.all_ships.update()
        self.allied_laser_beams.update()
        self.hostile_laser_beams.update()
        self.animations.update()
        
    def draw_game_state(self):
        '''Draws updated game state by wiping the game's main surface,
        drawing all the game's sprite groups and then flipping the game's main
        surface to display the drawings.'''
        
        # draw new game state    
        self.screen.blit(self.background_image,(0,0)) # paint over old game state
        
        self.all_ships.draw(self.screen) # draw all sprites
        self.allied_laser_beams.draw(self.screen) # draw player lasers
        self.hostile_laser_beams.draw(self.screen) # draw enemy lasers
        self.animations.draw(self.screen) # draw animations
                   
        # flip canvas
        pg.display.flip()
        
    def _sync_player_(self,player_sprite):
        '''Takes a ShipSprite class object and syncs its _d_speed and _d_angle
        attributes with the keyboard state. This is to avoid weird movement 
        when arrow keys are pressed while player is spawned.'''
        
        pressed_keys = pg.key.get_pressed()
        
        # sync player angle attributes
        if pressed_keys[pg.K_LEFT]:
            player_sprite._d_angle += player_sprite._d_angle_degrees_per_frame
        if pressed_keys[pg.K_RIGHT]:
            player_sprite._d_angle -= player_sprite._d_angle_degrees_per_frame
            
        # sync player speed attributes
        if pressed_keys[pg.K_UP]:
            player_sprite._d_speed += player_sprite._d_speed_pixel_per_frame
        if pressed_keys[pg.K_DOWN]:
            player_sprite._d_speed -= player_sprite._d_speed_pixel_per_frame
        
    def spawn_player(self,
                     center = np.array([900,300]),
                    angle=0,
                    speed=200,
                    d_angle_degrees_per_second = 150,
                    d_speed_pixel_per_second = 10,
                    max_speed_pixel_per_second = 400):
        
        '''Creates a new PlayerShipSprite object and adds it to the game.'''        
        
        player = ShipSprite(self.fps,
                          self.screen,
                          self.allied_images,
                          self.allied_gun_offsets,
                          self.allied_fire_modes,
                          self.allied_laser_beams,
                          self.allied_laser_sound,
                          self.allied_laser_images,
                          1.2, # laser range in seconds
                          150, # laser speed in pixel per second
                          2, # laser rate of fire in seconds
                          self.allied_muzzle_images,
                          self.allied_muzzle_spi, # seconds per image for muzzle flash
                          self.explosion_sound, # sound of explosion animation
                          self.explosion_images,
                          self.explosion_spi, # seconds per image for explosions animation at death
                          self.allied_engine_offsets,
                          self.engine_images,
                          self.engine_spi,
                          self.animations,
                          (self.allied_ships,self.all_ships),
                          center = center,
                          angle = angle,
                          speed = speed,
                          d_angle_degrees_per_second = d_angle_degrees_per_second,
                          d_speed_pixel_per_second = d_speed_pixel_per_second,
                          max_speed_pixel_per_second = max_speed_pixel_per_second)
        
        self._sync_player_(player)

        return player
    
    def spawn_ally(self,
                   center = np.array([1200,500]),
                   angle = 180,
                   speed = 200,
                   d_angle_degrees_per_second = 150,
                    d_speed_pixel_per_second = 10,
                    max_speed_pixel_per_second = 350):
        '''Creates a new allied AIShipSprite and adds it to the game.'''
        
        AIShipSprite(self.fps,
                        self.screen, # main screen
                        self.allied_images, # sequence with ShipSprite's skin
                        self.allied_gun_offsets,
                        self.allied_fire_modes,# 
                        self.allied_laser_beams,
                        self.allied_laser_sound, # pygame sound object; laser fire sound
                        self.allied_laser_images, # sequence with laser beam skin
                        1.2,
                        150,
                        2, # laser rate of fire in shots/second
                        self.allied_muzzle_images, # sequence of images for muzzle flash animation
                        self.allied_muzzle_spi, # seconds per image for muzzle flash animation
                        self.explosion_sound,
                        self.explosion_images,
                        self.explosion_spi,
                        self.allied_engine_offsets,
                        self.engine_images,
                        self.engine_spi,
                        self.animations,
                        #player,
                        self.piloting_cone_sine,
                        self.gunning_cone_sine,
                        (self.allied_ships, self.all_ships),
                        hostile_ships_group = self.hostile_ships, # group of hostile ships sprites
                        center = center,
                        angle=angle,
                        speed=speed,
                        d_angle_degrees_per_second = d_angle_degrees_per_second,
                        d_speed_pixel_per_second = d_speed_pixel_per_second,
                        max_speed_pixel_per_second = max_speed_pixel_per_second)
                    
    
    def spawn_hostile(self,
                    center = np.array([1200,50]),
                    angle=0,
                    speed=200,
                    d_angle_degrees_per_second = 150,
                    d_speed_pixel_per_second = 10,
                    max_speed_pixel_per_second = 350):
        
        '''Creates a new hostile AIShipSprite and adds it to the game.'''
        
        AIShipSprite(self.fps,
                        self.screen, # main screen
                        self.hostile_images, # sequence with ShipSprite's skin
                        self.hostile_gun_offsets,
                        self.hostile_fire_modes,# 
                        self.hostile_laser_beams,
                        self.hostile_laser_sound, # pygame sound object; laser fire sound
                        self.hostile_laser_images, # sequence with laser beam skin
                        1.2,
                        150,
                        2, # laser rate of fire in shots/second
                        self.hostile_muzzle_images, # sequence of images for muzzle flash animation
                        self.hostile_muzzle_spi, # seconds per image for muzzle flash animation
                        self.explosion_sound,
                        self.explosion_images,
                        self.explosion_spi,
                        self.hostile_engine_offsets,
                        self.engine_images,
                        self.engine_spi,
                        self.animations,
                        #player,
                        self.piloting_cone_sine,
                        self.gunning_cone_sine,
                        (self.hostile_ships, self.all_ships),
                        hostile_ships_group = self.allied_ships, # group of hostile ships sprites
                        center = center,
                        angle=angle,
                        speed=speed,
                        d_angle_degrees_per_second = d_angle_degrees_per_second,
                        d_speed_pixel_per_second = d_speed_pixel_per_second,
                        max_speed_pixel_per_second = max_speed_pixel_per_second)
        
    def spawn_ai_squadron(self,
                       side,
                       centers,
                       angles,
                       speeds,
                       d_angle_degrees_per_seconds,
                       max_speed_pixel_per_seconds):
        '''Util function to spawn a group of allied or hostile ships. Usually
        used at beginning of game.'''
        
        for center, angle, speed, d_angle, max_speed in zip(centers,
                                                            angles,
                                                            speeds,
                                                            d_angle_degrees_per_seconds,
                                                            max_speed_pixel_per_seconds):
            if side == 'allied':
                self.spawn_ally(center=center,
                                angle=angle,
                                speed=speed,
                                d_angle_degrees_per_second=d_angle,
                                max_speed_pixel_per_second=max_speed)
                
            elif side == 'hostile':
                self.spawn_hostile(center=center,
                                angle=angle,
                                speed=speed,
                                d_angle_degrees_per_second=d_angle,
                                max_speed_pixel_per_second=max_speed)
        
        
    def handle_collisions(self):
        '''Checks for collisions between player sprite and enemy lasers, as well
        as enemy sprites and player lasers. Terminates any sprites that were
        shot down. Records the time of the kill.'''

        ally_down = False
        hostile_down = False

        # check for enemy kills
        hit_allies = groupcollide(self.allied_ships,
                                      self.hostile_laser_beams,
                                      False,
                                      True,
                                      collide_mask)
        
        for hit_ally in hit_allies:
            # update hit ship's hit points attribute
            hit_ally._hit_points -= 1
            print('ally hit!')
            print('ally hit points left:',hit_ally._hit_points)
            
            # if ship has no more hit points left, destroy and set flag
            if not hit_ally._hit_points:
                hit_ally.kill()
                ally_down = True
        
        # check for player kills
        hit_hostiles = groupcollide(self.hostile_ships,
                                      self.allied_laser_beams,
                                      False,
                                      True,
                                      collide_mask)
        
        for hit_hostile in hit_hostiles:
            # update hit ship's hit points attribute
            hit_hostile._hit_points -= 1
            print('hostile hit!')
            print('hostile hit points left:',hit_hostile._hit_points)
            
            # if ship has no more hit points left, destroy and flag
            if not hit_hostile._hit_points:
                hit_hostile.kill()
                hostile_down = True
            
        return hostile_down, ally_down
            
            
def main():
    # make sure directory is repo head
    os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter')
    
    
    Game()
    
if __name__=='__main__':
    main()