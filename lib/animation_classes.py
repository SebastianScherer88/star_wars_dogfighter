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
 
#from pygame.sprite import Sprite, Group
from sprite_classes import MaskedSprite, BasicSprite
from pygame.sprite import Group
 
import pygame as pg
import numpy as np

import sys

class BasicAnimationNew(BasicSprite):
    '''Base class for animations used in game.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 seconds_per_image,
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
            seconds_per_image: number of seconds each image of the animation sequence will be shown.
                    (each image will be shown for the same duration)
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
                    is set to true. Default to (255,255,255), which corresponds to the color white.
            *groups: tuple of pygame Group objects. The sprite will add itself to each of these
                    when initialized.'''
                    
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
        
        # initialize frame counter
        self.frames_passed = 1
        
        # set sequence control attributes
        frames_per_image = float(self._fps) * seconds_per_image # get frames per images
        
        # construct list of frame count intervals, where one interval ~= one image from animation sequence
        n_images = len(original_images) # get number of images
        lowers = np.linspace(0,(n_images-1)*frames_per_image,n_images) # get lower boundaries for intervals
        uppers = np.linspace(frames_per_image,n_images*frames_per_image,n_images) # get upper boundaries for intervals
                            
        self.frame_image_intervals = [(lower,upper) for (lower,upper) in zip(lowers, # make list of intervals
                                                                              uppers)]     

        
    def get_interval_index(self,value,intervals):
        '''Helper function that takes a value and a list of intervals. Determines
        which interval the value lies in and returns the list index of that interval.
        If value lies in none of the intervals, returns False.'''
        
        for i,(lower,upper) in enumerate(intervals):
            if lower < value <= upper:
                
                return i + 1
            
        return False
        
    def update(self):
        '''base class update method plus checks & handling of image sequence & animation lifetime.'''
                
        # update frame counter
        self.frames_passed += 1
        
        # get current image index
        image_number = self.get_interval_index(self.frames_passed,
                                               self.frame_image_intervals)
        
        # if index is 'False', the time is up; terminate animation
        if not image_number:
            self.kill()
        # actual index is returned; perform base class update on appropriate image sequence element
        else:
            self._image_index = image_number - 1
            # call base class update
            BasicSprite.update(self)

class BasicAnimation(MaskedSprite):
    
    def __init__(self,
                 screen,
                 animation_meta_data,
                 animation_sound_object,
                 frames_per_second,
                 *groups,
                 angle=0,
                 speed=0,
                 center=np.array([0,0]).astype('float')):
        
        MaskedSprite.__init__(self,
                             screen,
                             animation_meta_data,
                             *groups,
                             angle=angle,
                             speed=speed,
                             center=center)
        
        # load sound file specified in metadat and play
        #animation_sound = pg.mixer.Sound(file=animation_meta_data['sound_path'])
        #animation_sound.play() # play on any channel available
        
        animation_sound_object.play()
        
        # set last image index
        self.last_image_index = len(self._original_images) - 1
        
        # get frames per image ratio
        self.frames_per_image = frames_per_second * animation_meta_data['seconds_per_image']
        
        # start counter
        self.counter = 1
        
    def update(self):
        '''Updates counter. Depending on counter:
            - does nothing
            - changes image
            - end animation by terminating sprite object'''
            
        self.counter += 1
        
        # Check if image needs to be updated / animation has ended
        if self.counter % int(self.frames_per_image) == 0:
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
    spi = 0.08 # seconds per image for animation
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
