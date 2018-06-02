# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 14:00:12 2018

@author: bettmensch
"""

'''This file contains experimental animation classes to be used in the game
 STAR WARS DOGFIGHTER.
 
 Idea: start with a basic type of animation for unmoveable animations (like an
 explosion). If that works try writing a moveable animation which can track another
 sprites movement and stay attached to it, i.e. have a constant position relative to that
 sprite through time (like gun flashes, missile propulsion, engine fire etc.)'''
 
from pygame.sprite import Sprite, Group
 
import pygame as pg

import sys
 
class BasicAnimation(Sprite):
    
    def __init__(self,
                 x,
                 y,
                 seconds_per_image,
                 frames_per_second,
                 *groups):
        
        pg.sprite.Sprite.__init__(self,*groups)
        
        # load and attach the explosion images
        original_images = []
        
        for i in range(9):
            index = i + 1
            image_path = './graphics/explosion' + str(index) + '.bmp'
            image = pg.image.load(image_path)
            image.set_colorkey((255,255,255)) # make image transparent
            original_images.append(image)
        
        self._original_images = original_images

        # make first image of sequence the sprite surface  
        self.image_index = 0
        self.image = self._original_images[self.image_index]
        
        # create, position and attach positional rect based on passed x&y image dimensions
        rect_size = self.image.get_size()
        self.rect = pg.Rect((x, y), rect_size)
        
        # attach sequence length (in images)
        self.last_image_index = len(self._original_images) - 1
        
        # get frames per image ratio
        self.frames_per_image = frames_per_second * seconds_per_image
        
        # start counter
        self.counter = 1
        
    def update(self):
        '''Updates counter. Depending on counter:
            - does nothing
            - changes image
            - end animation by terminating sprite object'''
            
        self.counter += 1
        
        # Check if image needs to be updated / animation has ended
        if self.counter % self.frames_per_image == 0:
            # if end of animation is NOT reached, continue animation
            if self.image_index < self.last_image_index:
                self.image_index += 1 # update image index
                self.image = self._original_images[self.image_index] # update animaion surface
            # if end of animation IS reached terminate animation sprite
            elif self.image_index == self.last_image_index:
                self.kill() # cleanly remove animation sprite
        

def main():
    '''Runs an animation demo of above class.'''

    # intialize pygame
    pg.init()
        
    # create clock    
    clock = pg.time.Clock()
    
    white = 255, 255, 255
    fps = 60 # frames per second for pygame
    spi = 0.1 # seconds per image for animation
    #frames_between_animation = 500 # pause between enemy death and spawning of new enemy in seconds
    
    # initialize main screen
    size = width, height = 1040, 740 # screen size
    screen = pg.display.set_mode(size)
    
    # initialize empty animation group
    animation_group = Group()
    
    # create animation
    BasicAnimation(520,
                   370,
                   spi,
                   fps,
                   animation_group)
    
    # start main game loop
    while True:
        # check for exit events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        
        # update sprites
        animation_group.update()
        
        # draw new game state    
        screen.fill(white) # paint over old game state
        
        animation_group.draw(screen) # draw all player sprite
                   
        # flip canvas
        pg.display.flip()       
            
        # control framerate
        clock.tick(fps)                

if __name__ == '__main__':
    main()
