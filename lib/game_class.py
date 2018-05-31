# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:09:47 2018

@author: Atreju Maischberger
"""

# demo gam states here
import sys

import pygame as pg

import numpy as np

from pygame.sprite import Group, collide_mask, spritecollide, groupcollide
from sprite_classes import PlayerSprite, EnemySprite

class Game(object):
    
    def __init__(self,screen_width=800,screen_height=500):
        '''Initializes the game object and also the game'''
        
        pg.init()
        
        # create clock    
        clock = pg.time.Clock()
        
        white = 255, 255, 255
        fps = 40
        enemy_down_time = 500 # pause between enemy death and spawning of new enemy in seconds
        
        # initialize main screen
        size = width, height = 1040, 740 # screen size
        screen = pg.display.set_mode(size)
        
        player_sprite = Group()
        player_lasers = Group()
        enemy_sprite = Group()
        enemy_lasers = Group()
        
        # create player sprite
        player = PlayerSprite(screen,'x_wing',player_lasers,
                              player_sprite,
                              angle=-45)
        
        # create first enemy sprite
        EnemySprite(screen,'tie_fighter',enemy_lasers,player,
                    enemy_sprite,
                    angle=-45,center=[200,400],speed=5)
        
        kill_confirmed= False
        
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            # update sprites
            player_sprite.update()
            enemy_sprite.update()
            
            # update lasers
            player_lasers.update()
            enemy_lasers.update()
            
            # draw new game state    
            screen.fill(white) # paint over old game state
            
            player_sprite.draw(screen) # draw all player sprite
            player_lasers.draw(screen) # draw all player laser sprites
            
            enemy_sprite.draw(screen) # draw all enemy sprite
            enemy_lasers.draw(screen) # draw all enemy laser sprite
                       
            # flip canvas
            pg.display.flip()
            
            # check for collisions
            if spritecollide(player,enemy_sprite,True,collided=collide_mask) or \
                            spritecollide(player,enemy_lasers,True,collided=collide_mask):
                # if player collides with enemy or is shot down, end game
                pg.quit()
                sys.exit()
                
            elif groupcollide(enemy_sprite,player_lasers,True,True,collided=collide_mask):    
                # mark down time of kill shot
                kill_confirmed = True
                kill_time = pg.time.get_ticks()
                
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
                            EnemySprite(screen,'tie_fighter',enemy_lasers,player,
                                        enemy_sprite,
                                        angle=-45,center=enemy_center,speed=5)
                            
                            # break loop when done
                            too_close = False
        
            
            # control pace
            clock.tick(fps)
            
def main():
    # create new game
    Game()
    
if __name__=='__main__':
    main()