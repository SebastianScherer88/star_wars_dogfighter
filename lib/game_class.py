# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:09:47 2018

@author: Atreju Maischberger
"""

# demo gam states here
import sys
import os

import pygame as pg
import numpy as np
import yaml

from pygame.sprite import Group, collide_mask, groupcollide
from sprite_classes import PlayerShipSprite, EnemyShipSprite

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
        
        # load images
        self.player_images = [pg.image.load('./graphics/tiefighter.bmp')]
        self.enemy_images = [pg.image.load('./graphics/awing.bmp')]
        self.laser_images_red = [pg.image.load('./graphics/redlaser.bmp')]
        self.laser_images_green = [pg.image.load('./graphics/greenlaser.bmp')]
        self.explosion_images = [pg.image.load('./graphics/explosion' + str(i+1) + '.bmp') for i in range(9)]
        
        # load metadata
        with open('./meta/sprite_meta_data.yaml','r') as sprite_meta_data_yaml:
            sprite_meta_data = yaml.load(sprite_meta_data_yaml)
            
        # player cannon positions
        self.player_cannon_positions = sprite_meta_data['tie_fighter']['cannon_tip_positions']
        self.enemy_cannon_positions = sprite_meta_data['a_wing']['cannon_tip_positions']
        
        # load sounds
        self.laser_sound = pg.mixer.Sound('./sounds/missile.wav')
        self.explosion_sound = pg.mixer.Sound('./sounds/explosion.wav')
        
        # initialize empty sprite groups
        self.all_sprites = Group()
        
        # player's groups
        self.player_sprite = Group()
        self.player_laser_sprites = Group()
        
        # enemy groups
        self.enemy_sprites = Group()
        self.enemy_laser_sprites = Group()
        
        # explosion group
        self.explosion_animations = Group()
        
        
        # create player sprite and add to relevant groups / provide with relevant groups
        player = self.spawn_player(center=np.array([1000,300]),
                                   angle=180,
                                   speed=15000,
                                   max_speed_pixel_per_second=18000)
        
        # create three enemies
        self.spawn_enemy(player,
                         center=np.array([40,50]),
                         speed=12000)# enemy #1
        self.spawn_enemy(player,
                         center=np.array([40,250]),
                        speed=12000) # enemy #1
        self.spawn_enemy(player,
                         center=np.array([40,450]),
                        speed=12000) # enemy #1
                                        
                        
        # initialize enemy down time so that 2 enemies are spawned at beginning of game
        enemy_down = False
        player_down = False
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
            # spawn enemies if needed
            if enemy_down:
                # create first two enemy sprites and add to relevant groups / provide with relevant groups
                self.spawn_enemy(player,
                                 speed=12000) # enemy #1

                
            if player_down:
                # reanimate player
                player = self.spawn_player()
                
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
        self.explosion_animations.update()
        
    def draw_game_state(self):
        '''Draws updated game state by wiping the game's main surface,
        drawing all the game's sprite groups and then flipping the game's main
        surface to display the drawings.'''
        
        # draw new game state    
        self.screen.blit(self.background_image,(0,0)) # paint over old game state
        
        self.all_sprites.draw(self.screen) # draw all sprites
        self.player_laser_sprites.draw(self.screen) # draw player lasers
        self.enemy_laser_sprites.draw(self.screen) # draw enemy lasers
        self.explosion_animations.draw(self.screen) # draw explosions
                   
        # flip canvas
        pg.display.flip()
        
    def spawn_player(self,
                     center = np.array([900,300]),
                    angle=0,
                    speed=20000,
                    d_angle_degrees_per_second = 100,
                    d_speed_pixel_per_second = 500,
                    max_speed_pixel_per_second = 30000):
        
        '''Creates a new PlayerShipSprite object and adds it to the game.'''
        
        player = PlayerShipSprite(self.fps,
                 self.screen,
                 self.player_images,
                 self.player_cannon_positions,
                 self.player_laser_sprites,
                 self.laser_sound,
                 self.laser_images_green,
                 1.2 , # laser range in seconds
                 15000, # laser speed in pixel per second
                 2, # laser rate of fire in seconds
                 self.explosion_animations, # explosion group
                 self.explosion_sound, # sound of explosion animation
                 self.explosion_images,
                 0.15, # seconds per image for explosions animation at death
                 (self.player_sprite,self.all_sprites), # groups that player will be added to
                 center = center,
                 angle = angle,
                 speed = speed,
                 d_angle_degrees_per_second = d_angle_degrees_per_second,
                 d_speed_pixel_per_second = d_speed_pixel_per_second,
                 max_speed_pixel_per_second = max_speed_pixel_per_second)
        
        return player
    
    def spawn_enemy(self,
                    player,
                    center = np.array([1200,50]),
                    angle=0,
                    speed=20000,
                    d_angle_degrees_per_second = 100,
                    d_speed_pixel_per_second = 500,
                    max_speed_pixel_per_second = 20000):
        
        '''Creates a new EnemyShipSprite and adds it to the game.'''
        
        EnemyShipSprite(self.fps,
                        self.screen,
                        self.enemy_images,
                        self.enemy_cannon_positions,
                        self.enemy_laser_sprites,
                        self.laser_sound,
                        self.laser_images_red,
                        1,
                        10000,
                        2,
                        self.explosion_animations,
                        self.explosion_sound,
                        self.explosion_images,
                        0.15,
                        player,
                        0.1,
                        0.1,
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