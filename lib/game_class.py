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
from sprite_classes import PlayerShipSprite, EnemyShipSprite, MissileSprite
from animation_classes import BasicAnimation, BasicAnimationNew

class Game2(object):
    
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
        enemy_images = [pg.image.load('./graphics/tie_fighter.bmp')]
        laser_images_red = [pg.image.load('./graphics/redlaser.bmp')]
        laser_images_green = [pg.image.load('./graphics/greenlaser.bmp')]
        explosion_images = [pg.image.load('./graphics/explosion' + str(i+1) + '.bmp') for i in range(9)]
        
        # load metadata
        with open('./meta/sprite_meta_data.yaml','r') as sprite_meta_data_yaml:
            sprite_meta_data = yaml.load(sprite_meta_data_yaml)
            
        # player cannon positions
        player_cannon_positions = sprite_meta_data['a_wing']['cannon_tip_positions']
        
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
        PlayerShipSprite(fps,
                 screen,
                 player_images,
                 player_cannon_positions,
                 player_laser_sprites,
                 laser_sound,
                 laser_images_red,
                 1.5 , # laser range in seconds
                 10, # laser speed in pixel per second
                 2, # laser rate of fire in seconds
                 explosion_animations, # explosion group
                 explosion_sound, # sound of explosion animation
                 explosion_images,
                 0.15, # seconds per image for explosions animation at death
                 (player_sprite,all_sprites), # groups that player will be added to
                 center = np.array([screen_width/4],screen_height/2),
                 angle = 0,
                 speed = 30,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 100) 
        
        # create explosion animation
        BasicAnimationNew(fps,
                 screen,
                 explosion_images,
                 0.2,
                 (explosion_animations,all_sprites),
                 center = np.array([400,400]),
                 angle = 0,
                 speed = 0)
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            # update all sprites
            all_sprites.update()
            
            # draw new game state    
            screen.fill(white) # paint over old game state
            
            all_sprites.draw(screen) # draw all sprites
                       
            # flip canvas
            pg.display.flip()
                        
            # control pace
            clock.tick(fps)

class Game(object):
    
    def __init__(self,screen_width=1200,screen_height=600,
                 all_sprite_meta_data=None,
                 all_animation_meta_data=None):
        '''Initializes the game object and also the game'''
        
        # initialize pygame (handles pretty much eveything)
        pg.init()
        
        # initialize pygame mixer (handles audio playback)
        pg.mixer.init()
        
        # load sound objects
        explosion_sound = pg.mixer.Sound(file=all_animation_meta_data['explosion']['sound_path'])
        laser_sound = pg.mixer.Sound(file=all_sprite_meta_data['red_laser']['sound_path'])
        
        # create clock    
        clock = pg.time.Clock()
        
        white = 255, 255, 255
        fps = 60
        enemy_down_time = 2 # pause between enemy death and spawning of new enemy in seconds
        
        # initialize main screen
        size = width, height = 1040, 740 # screen size
        screen = pg.display.set_mode(size)
        
        # initialize empty sprite groups
        all_sprites = Group()
        player_sprite = Group()
        player_lasers = Group()
        enemy_sprite = Group()
        enemy_lasers = Group()
        explosions = Group()
        
        # create player sprite and add to relevant groups / provide with relevant groups
        player = PlayerSprite(screen,
                              all_sprite_meta_data['x_wing'],
                              all_sprite_meta_data['red_laser'],
                              player_lasers,
                              laser_sound,
                              (player_sprite,all_sprites),
                              angle=-45)
        
        # create first enemy sprite and add to relevant groups / provide with relevant groups
        EnemySprite(screen,
                    all_sprite_meta_data['tie_fighter'],
                    all_sprite_meta_data['green_laser'],
                    enemy_lasers,
                    laser_sound,
                    player,
                    (enemy_sprite,all_sprites),
                    angle=-45,
                    center=[200,400],
                    speed=5)
        
        
        kill_confirmed= False
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            # update all sprites
            all_sprites.update()
            player_lasers.update()
            enemy_lasers.update()
            
            # update explosions
            explosions.update()
            
            # draw new game state    
            screen.fill(white) # paint over old game state
            
            all_sprites.draw(screen) # draw all sprites
            player_lasers.draw(screen) # draw player lasers
            enemy_lasers.draw(screen) # draw enemy lasers
            explosions.draw(screen) # draw explosion animation
                       
            # flip canvas
            pg.display.flip()
            
            # check for player collisions with enemy sprites and enemy lasers
            collided_enemy_sprites = groupcollide(player_sprite,
                                                   enemy_sprite,
                                                   True,
                                                   True,
                                                   collided=collide_mask)
            collided_enemy_lasers = groupcollide(player_sprite,
                                                 enemy_lasers,
                                                 True,
                                                 True,
                                                 collided=collide_mask)
            
            # if player collides with either laser or enemy sprite, create explosion at player position
            if collided_enemy_sprites or collided_enemy_lasers:
                BasicAnimation(screen,
                               all_animation_meta_data['explosion'],
                                explosion_sound,
                                fps,
                                explosions,
                                center=player._center)
                
                # if player collides with enemy sprite in particular, create explosion at enemy position
                for collided_enemy_sprite in collided_enemy_sprites:
                    BasicAnimation(screen,
                                   all_animation_meta_data['explosion'],
                                    explosion_sound,
                                    fps,
                                    explosions,
                                    center=collided_enemy_sprite._center)
            
            # check for enemy collisions with player lasers
            downed_enemy_sprites = groupcollide(enemy_sprite,player_lasers,True,True,collided=collide_mask)
            
            if downed_enemy_sprites:
                # mark down time of kill shot
                kill_confirmed = True
                kill_time = pg.time.get_ticks()
                
                # create explosion at location of killed enemy sprites
                for downed_enemy_sprite in downed_enemy_sprites:
                    BasicAnimation(screen,
                                   all_animation_meta_data['explosion'],
                                    explosion_sound,
                                    fps,
                                    explosions,
                                    center=downed_enemy_sprite._center)
                
            # spawn new enemy if necessary
            if kill_confirmed:
                # check if enough time has passed since kill
                now_time = pg.time.get_ticks()
                if (now_time - kill_time) / 1000 > enemy_down_time:
                    # reset confirmed kill flag
                    kill_confirmed = False
                    
                    # start spawning procedure
                    too_close = True
                    
                    while too_close:
                        
                        # spawn enemy at random location
                        enemy_center = np.random.uniform(0,1,2) * np.array([width,height]).astype('float')
                        
                        # if enemy has safety distance from player, proceed with spawning
                        if np.linalg.norm(player._center-enemy_center,ord=1) > min(width/2,height/2):
                            # spawn enemy
                            EnemySprite(screen,
                                        all_sprite_meta_data['tie_fighter'],
                                        all_sprite_meta_data['green_laser'],
                                        enemy_lasers,
                                        laser_sound,
                                        player,
                                        (enemy_sprite,all_sprites),
                                        angle=-45,
                                        center=[200,400],
                                        speed=5)
                            
                            
                            # break loop when done
                            too_close = False
        
            
            # control pace
            clock.tick(fps)
            
def main():
    # make sure directory is repo head
    os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter')
    
    # get game meta data for sprites
    #with open('./meta/sprite_meta_data.yaml','r') as sprite_meta_data_file:
    #    sprite_meta_data = yaml.load(sprite_meta_data_file)
        
    # get game meta dat for animations
    #with open('./meta/animation_meta_data.yaml','r') as animation_meta_data_file:
    #    animation_meta_data = yaml.load(animation_meta_data_file)
    
    # create new game with all the meta data
    #Game(all_sprite_meta_data=sprite_meta_data,
    #     all_animation_meta_data=animation_meta_data)
    
    Game2()
    
if __name__=='__main__':
    main()