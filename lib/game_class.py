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
        player_ship, player_laser = 'awing', 'red'
        enemy_ship, enemy_laser = 'tiefighter', 'green'
        
        # set game attributes from meta data for player
        
        # skin specific
        self.player_images = [pg.image.load(image_path) for image_path in skins_meta_data[player_ship]['image_paths']]
        self.player_gun_offsets = np.array(skins_meta_data[player_ship]['gun_offsets']).astype('float')
        self.player_engine_offsets = np.array(skins_meta_data[player_ship]['engine_offsets']).astype('float')
        self.player_fire_modes = skins_meta_data[player_ship]['fire_modes']
        
        # laser specific
        self.player_laser_images = [pg.image.load(image_path) for image_path in skins_meta_data[player_laser]['image_paths']]
        self.player_laser_sound = pg.mixer.Sound(animations_meta_data[player_laser]['sound'])
        self.player_muzzle_images = [pg.image.load(image_path) for image_path in animations_meta_data[player_laser]['image_paths']]
        self.player_muzzle_spi = animations_meta_data[player_laser]['spi']
        
        
        # set game attributes from meta data for enemies
        
        # behavioural
        self.enemy_piloting_cone_sine = 0.1
        self.enemy_gunning_cone_sine = 0.1
        
        # skin specific
        self.enemy_images = [pg.image.load(image_path) for image_path in skins_meta_data[enemy_ship]['image_paths']]
        self.enemy_gun_offsets = np.array(skins_meta_data[enemy_ship]['gun_offsets']).astype('float')
        self.enemy_engine_offsets = np.array(skins_meta_data[enemy_ship]['engine_offsets']).astype('float')
        self.enemy_fire_modes = skins_meta_data[enemy_ship]['fire_modes']
        
        # laser specific
        self.enemy_laser_images = [pg.image.load(image_path) for image_path in skins_meta_data[enemy_laser]['image_paths']]
        self.enemy_laser_sound = pg.mixer.Sound(animations_meta_data[enemy_laser]['sound'])
        self.enemy_muzzle_images = [pg.image.load(image_path) for image_path in animations_meta_data[enemy_laser]['image_paths']]
        self.enemy_muzzle_spi = animations_meta_data[enemy_laser]['spi']
        
        # load universal game animation attributes from meta data
        
        # explosion
        self.explosion_images = [pg.image.load(image_path) for image_path in animations_meta_data['explosion']['image_paths']]
        self.explosion_sound = pg.mixer.Sound(animations_meta_data['explosion']['sound'])
        self.explosion_spi = animations_meta_data['explosion']['spi']
        
        # engine flame
        self.engine_images = [pg.image.load(image_path) for image_path in animations_meta_data['engine']['image_paths']]
        self.engine_spi = animations_meta_data['engine']['spi']
        
        # initialize empty sprite groups
        self.all_sprites = Group()
        
        # player's groups
        self.player_sprite = Group()
        self.player_laser_sprites = Group()
        
        # enemy groups
        self.enemy_sprites = Group()
        self.enemy_laser_sprites = Group()
        
        # animation group
        self.animations = Group()        
        
        # create player sprite and add to relevant groups / provide with relevant groups
        player = self.spawn_player(center=np.array([1000,300]),
                                   angle=180,
                                   speed=250,
                                   d_angle_degrees_per_second = 150,
                                   max_speed_pixel_per_second=360)
        
        # create three enemies
        self.spawn_enemy(player,
                         center=np.array([40,50]),
                         speed=300,
                         d_angle_degrees_per_second = 150,
                         max_speed_pixel_per_second=300)# enemy #1
        #self.spawn_enemy(player,
        #                 center=np.array([40,450]),
        #                 speed=300,
        #                 d_angle_degrees_per_second = 150,
        #                 max_speed_pixel_per_second=300)# enemy #1
        #self.spawn_enemy(player,
        #                 center=np.array([40,450]),
        #                speed=200) # enemy #3
                                        
                        
        # initialize enemy down time so that 2 enemies are spawned at beginning of game
        enemy_down = False
        player_down = False
        
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
            if enemy_down:
                # create first two enemy sprites and add to relevant groups / provide with relevant groups
                self.spawn_enemy(player,
                                 speed=300,
                                 d_angle_degrees_per_second = 150,
                                 max_speed_pixel_per_second=300) # enemy #1

                
            if player_down:
                # reanimate player
                player = self.spawn_player(speed=300,
                                           d_angle_degrees_per_second = 150,
                                           max_speed_pixel_per_second=360)
                
                # update enemies target computers
                for enemy in self.enemy_sprites:
                    enemy._player_sprite = player
                
            # update game state
            self.update_game_state()
            
            # draw update game state to screen
            self.draw_game_state()
            
            # check and handle collisions
            enemy_down, player_down = self.handle_collisions()
                        
            # control pace
            self.clock.tick(fps)
            
    def update_game_state(self):
        '''Updates the game state by updating all the game's sprite groups.'''
        
        self.all_sprites.update()
        self.player_laser_sprites.update()
        self.enemy_laser_sprites.update()
        self.animations.update()
        
    def draw_game_state(self):
        '''Draws updated game state by wiping the game's main surface,
        drawing all the game's sprite groups and then flipping the game's main
        surface to display the drawings.'''
        
        # draw new game state    
        self.screen.blit(self.background_image,(0,0)) # paint over old game state
        
        self.all_sprites.draw(self.screen) # draw all sprites
        self.player_laser_sprites.draw(self.screen) # draw player lasers
        self.enemy_laser_sprites.draw(self.screen) # draw enemy lasers
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
                          self.player_images,
                          self.player_gun_offsets,
                          self.player_fire_modes,
                          self.player_laser_sprites,
                          self.player_laser_sound,
                          self.player_laser_images,
                          1.2, # laser range in seconds
                          150, # laser speed in pixel per second
                          2, # laser rate of fire in seconds
                          self.player_muzzle_images,
                          self.player_muzzle_spi, # seconds per image for muzzle flash
                          self.explosion_sound, # sound of explosion animation
                          self.explosion_images,
                          self.explosion_spi, # seconds per image for explosions animation at death
                          self.player_engine_offsets,
                          self.engine_images,
                          self.engine_spi,
                          self.animations,
                          (self.player_sprite,self.all_sprites),
                          center = center,
                          angle = angle,
                          speed = speed,
                          d_angle_degrees_per_second = d_angle_degrees_per_second,
                          d_speed_pixel_per_second = d_speed_pixel_per_second,
                          max_speed_pixel_per_second = max_speed_pixel_per_second)
        
        self._sync_player_(player)

        return player
    
    def spawn_enemy(self,
                    player,
                    center = np.array([1200,50]),
                    angle=0,
                    speed=200,
                    d_angle_degrees_per_second = 150,
                    d_speed_pixel_per_second = 10,
                    max_speed_pixel_per_second = 350):
        
        '''Creates a new EnemyShipSprite and adds it to the game.'''
        
        AIShipSprite(self.fps,
                        self.screen, # main screen
                        self.enemy_images, # sequence with ShipSprite's skin
                        self.enemy_gun_offsets,
                        self.enemy_fire_modes,# 
                        self.enemy_laser_sprites,
                        self.enemy_laser_sound, # pygame sound object; laser fire sound
                        self.enemy_laser_images, # sequence with laser beam skin
                        1.2,
                        150,
                        2, # laser rate of fire in shots/second
                        self.enemy_muzzle_images, # sequence of images for muzzle flash animation
                        self.enemy_muzzle_spi, # seconds per image for muzzle flash animation
                        self.explosion_sound,
                        self.explosion_images,
                        self.explosion_spi,
                        self.enemy_engine_offsets,
                        self.engine_images,
                        self.engine_spi,
                        self.animations,
                        player,
                        self.enemy_piloting_cone_sine,
                        self.enemy_gunning_cone_sine,
                        (self.enemy_sprites, self.all_sprites),
                        center = center,
                        angle=angle,
                        speed=speed,
                        d_angle_degrees_per_second = d_angle_degrees_per_second,
                        d_speed_pixel_per_second = d_speed_pixel_per_second,
                        max_speed_pixel_per_second = max_speed_pixel_per_second)
        
    def handle_collisions(self):
        '''Checks for collisions between player sprite and enemy lasers, as well
        as enemy sprites and player lasers. Terminates any sprites that were
        shot down. Records the time of the kill.'''

        player_down = False
        enemy_down = False

        # check for enemy kills
        downed_players = groupcollide(self.player_sprite,
                                      self.enemy_laser_sprites,
                                      True,
                                      True,
                                      collide_mask)
        
        for downed_player in downed_players:
            # terminate player sprite
            downed_player.kill()
            
            # set player down flag
            player_down = True
        
        # check for player kills
        downed_enemies = groupcollide(self.enemy_sprites,
                                      self.player_laser_sprites,
                                      True,
                                      True,
                                      collide_mask)
        
        for downed_enemy in downed_enemies:
            # terminate enemy psrite that was shot down
            downed_enemy.kill()
            
            # set enemy down flag
            enemy_down = True
            
        return enemy_down, player_down
            
            
def main():
    # make sure directory is repo head
    os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter')
    
    
    Game()
    
if __name__=='__main__':
    main()