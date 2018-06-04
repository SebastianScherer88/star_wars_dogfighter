# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 18:50:22 2018

@author: bettmensch
"""

import os
import yaml

os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter/meta')

# create explosion animation meta data
# needs:
#   - sound
#   - image_paths
#   - images_per_second


    

explosion_meta_data = {'image_paths':['./graphics/explosion1.bmp',
                                      './graphics/explosion2.bmp',
                                      './graphics/explosion3.bmp',
                                      './graphics/explosion4.bmp',
                                      './graphics/explosion5.bmp',
                                      './graphics/explosion6.bmp',
                                      './graphics/explosion7.bmp'
                                      './graphics/explosion8.bmp',
                                      './graphics/explosion9.bmp'],
                        'sounds':['./sounds/explosion.wav'],
                        'images_per_second':0.1}

animation_meta_data = {'explosion':explosion_meta_data}

with open('animation_meta_data.yaml','w') as animation_meta_data_file:
    yaml.dump(animation_meta_data,animation_meta_data_file)