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
from basic_sprite_class import BasicSprite
from math import pi, sin, cos
 
import numpy as np

class BasicAnimation(BasicSprite):
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
                 looping = False,
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
        
        # if animation looping?
        self.is_looping = looping
        
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
        
        # if index is 'False', the time is up; 
        if not image_number:
            if not self.is_looping:
                # animation is not of looping type and is out of type -> terminate
                self.kill()
            else:
                # animation is of looping type and is out of time -> restart from beginning
                self.frames_passed = 1
                self._image_index = 0
        # actual index is returned; perform base class update on appropriate image sequence element
        else:
            self._image_index = image_number - 1
        
        # call base class update
        BasicSprite.update(self)
        
class TrackingAnimation(BasicAnimation):
    
    '''Based on the BasicAnimation class, this animation type is designed to track a ShipSprite (based) object and
    keep a constant position w.r.t to that tracked Sprite. 
    
    NOTE:It does not update its own positional coordinates 
    incrementally like the ShipSprite (based) classes and the BasicAnimation class, but rather overrides its positional
    attributes completely ech frame, based on the tracked sprite's positional attributes. It should therefore always be
    initialized with initial_speed = 0; otherwise, the incremental velocity changes inherited from the BasicSprite class
    would cause the animation to loose track of its anchor sprite.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 seconds_per_image,
                 tracked_sprite,
                 original_offset,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 looping = False,
                 dynamic_angle = True,
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
            tracked_sprite: SpriteShip (based) type object that the animation will track to continuously
                        update its position and  visually stay 'attached' to that sprite.
            original_offset: Offset between tracked sprite's center and animation's center if angle==0.
                    Used to maintain relative position constant when tracked sprite rotates.
            center: initial position of center of sprite's rectangle (numpy float-type array of shape (2,)).
                    Sets the sprite's initial position on the 'screen' surface.
            is_transparent: transparency flag. If set, pixels colored in the 'transparent_color'
                    color argument in the surfaces contained in 'original_images' will be made transparent.
                    Default is True
            transparent_color: tuple specifiying the color key considered as transparent if 'is_transparent'
                    is set to true. Default to (255,255,255), which corresponds to the color white.
            *groups: tuple of pygame Group objects. The sprite will add itself to each of these
                    when initialized.'''
        
        # Note that speed and angle attributes inherited from BasicSprite
        # defualt to 0 if not passed to initializer
        BasicAnimation.__init__(self,
                                fps,
                                 screen,
                                 original_images,
                                 seconds_per_image,
                                 *groups,
                                 looping = looping,
                                 is_transparent = is_transparent,
                                 transparent_color = transparent_color)
        
        # attach dynamic angle attribute
        self._dynamic_angle = dynamic_angle
        
        # attach tracked sprite
        self._tracked_sprite = tracked_sprite
        
        # attach original offsets
        self._original_offset = original_offset
        
        
    def update(self):
        '''Updates the animations position and orientation based on tracked sprite.
        Then updates animation's rect and image attributes accordingly through the base
        class update().'''
        
        # first check if tracked ship is still alive; if not, kill self
        if not self._tracked_sprite._alive:
            self.kill()
        
        # get ._angle form tracked sprite if dynamic angle is toggled
        if self._dynamic_angle:
            self._angle = self._tracked_sprite._angle
        
        # get .center and offsets from tracked sprite
        self._center = self._tracked_sprite._center + self._get_rotated_offset()

        # before you call this, make sure:
        # self._speed == 0
        BasicAnimation.update(self) 
        
    def _get_rotated_offset(self):
        '''Rotate and return the original offset.'''
        
        # convert ship's current angle to radian
        radian_angle = self._angle * pi / 180
        
        # get rotation matrix for radian angle
        rotation_matrix = np.array([[cos(radian_angle), sin(radian_angle)],
                                   [- sin(radian_angle), cos(radian_angle)]])
        
        # rotate original offset attribute (counter-clockwise)
        rotated_offset = np.dot(rotation_matrix,
                                self._original_offset.T).T
                                
        return rotated_offset.reshape(2,)