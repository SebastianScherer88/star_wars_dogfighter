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
from animation_classes import BasicAnimation

class Game(object):
    
    def __init__(self,
                 screen_width=1200,
                 screen_height=600):
        '''Initializes the game object and also the game'''
        
        # initialize pygame (handles pretty much eveything)
        pg.init()
        
        # create clock    
        clock = pg.time.Clock()
        
        white = 255, 255, 255
        fps = 60
        
        # initialize main screen
        size = screen_width, screen_height # set screen size
        screen = pg.display.set_mode(size)
        
        # load images
        player_images = [pg.image.load('./graphics/awing.bmp')]
        enemy_images = [pg.image.load('./graphics/tiefighter.bmp')]
        laser_images_red = [pg.image.load('./graphics/redlaser.bmp')]
        laser_images_green = [pg.image.load('./graphics/greenlaser.bmp')]
        explosion_images = [pg.image.load('./graphics/explosion' + str(i+1) + '.bmp') for i in range(9)]
        
        # load metadata
        with open('./meta/sprite_meta_data.yaml','r') as sprite_meta_data_yaml:
            sprite_meta_data = yaml.load(sprite_meta_data_yaml)
            
        # player cannon positions
        player_cannon_positions = sprite_meta_data['a_wing']['cannon_tip_positions']
        enemy_cannon_positions = sprite_meta_data['tie_fighter']['cannon_tip_positions']
        
        # load sounds
        laser_sound = pg.mixer.Sound('./sounds/missile.wav')
        explosion_sound = pg.mixer.Sound('./sounds/explosion.wav')
        
        # initialize empty sprite groups
        all_sprites = Group()
        
        # player's groups
        player_sprite = Group()
        player_laser_sprites = Group()
        
        # enemy groups
        enemy_sprites = Group()
        enemy_laser_sprites = Group()
        
        # explosion group
        explosion_animations = Group()
        
        
        # create player sprite and add to relevant groups / provide with relevant groups
        player = PlayerShipSprite(fps,
                 screen,
                 player_images,
                 player_cannon_positions,
                 player_laser_sprites,
                 laser_sound,
                 laser_images_red,
                 1.5 , # laser range in seconds
                 10000, # laser speed in pixel per second
                 2, # laser rate of fire in seconds
                 explosion_animations, # explosion group
                 explosion_sound, # sound of explosion animation
                 explosion_images,
                 0.15, # seconds per image for explosions animation at death
                 (player_sprite,all_sprites), # groups that player will be added to
                 center = np.array([screen_width/4,screen_height/2]),
                 angle = 40,
                 speed = 3000,
                 d_angle_degrees_per_second = 100,
                 d_speed_pixel_per_second = 500,
                 max_speed_pixel_per_second = 30000) 
        
        EnemyShipSprite(fps,
                        screen,
                        enemy_images,
                        enemy_cannon_positions,
                        enemy_laser_sprites,
                        laser_sound,
                        laser_images_green,
                        1.5,
                        10000,
                        2,
                        explosion_animations,
                        explosion_sound,
                        explosion_images,
                        0.15,
                        player,
                        0.1,
                        0.1,
                        (enemy_sprites, all_sprites),
                        center = np.array([3*screen_width/4,screen_height/2]),
                        angle=0,
                        speed=20000,
                        d_angle_degrees_per_second = 100,
                        d_speed_pixel_per_second = 500,
                        max_speed_pixel_per_second = 20000)
                        
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            # update all sprites
            all_sprites.update()
            player_laser_sprites.update()
            enemy_laser_sprites.update()
            explosion_animations.update()
            
            # draw new game state    
            screen.fill(white) # paint over old game state
            
            all_sprites.draw(screen) # draw all sprites
            player_laser_sprites.draw(screen) # draw player lasers
            enemy_laser_sprites.draw(screen) # draw enemy lasers
            explosion_animations.draw(screen) # draw explosions
                       
            # flip canvas
            pg.display.flip()
            
            # check for player kills
            downed_enemies = groupcollide(enemy_sprites,player_laser_sprites,True,True,collide_mask)
            
            for downed_enemy in downed_enemies:
                downed_enemy.kill()
                
            # check for enemy kills
            downed_players = groupcollide(player_sprite,enemy_laser_sprites,True,True,collide_mask)
            
            for downed_player in downed_players:
                downed_player.kill()
                        
            # control pace
            clock.tick(fps)
            
def main():
    # make sure directory is repo head
    os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter')
    
    Game()
    
if __name__=='__main__':
    main()