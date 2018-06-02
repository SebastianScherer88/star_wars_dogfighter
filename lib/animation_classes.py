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
 
from sprite_classes import MaskedSprite
 
import pygame as pg
import numpy as np
 
class BasicAnimation(MaskedSprite):
    
    def __init__(self):
        return
