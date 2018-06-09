# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 18:50:22 2018

@author: bettmensch
"""

import os
import yaml

os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter/meta')



#----------------------------------------------
# [1] Create and save animation meta data
#----------------------------------------------

# each entry in the animation meta data needs:
#   - sound: path to sound file (optional)
#   - image_paths: list of paths to all images used to create sequence
#   - spi: seconds per image

animations_meta_data = {}

# create meta data for red laser muzzle flash animation
animations_meta_data['red'] = {'image_paths':['./graphics/red_muzzle_flash/red_muzzle_flash' + str(i+1) + '.bmp' for i in range(6)],
                                'sound':'./sounds/missile.wav',
                                'spi':0.02}

# create meta data for green laser muzzle flash animation
animations_meta_data['green'] = {'image_paths':['./graphics/green_muzzle_flash/green_muzzle_flash' + str(i+1) + '.bmp' for i in range(6)],
                                'sound':'./sounds/missile.wav',
                                'spi':0.02}

# create meta data for explosion animation
animations_meta_data['explosion'] = {'image_paths':['./graphics/explosion/explosion' + str(i+1) + '.bmp' for i in range(9)],
                                    'sound':'./sounds/explosion.wav',
                                    'spi':0.1}

# create meta data for engine flames
animations_meta_data['engine'] = {'image_paths':['./graphics/engine_flame/engine_flame' + str(i+1) + '.bmp' for i in range(4)],
                                    'spi':0.1}

with open('animations_meta_data.yaml','w') as animations_meta_data_file:
    yaml.dump(animations_meta_data,animations_meta_data_file)
    
#----------------------------------------------
# [2] Create and save sprite skin meta data
#----------------------------------------------

skins_meta_data = {}

# create meta data for awing skin
skins_meta_data['awing'] = {'image_paths':['./graphics/sprite_skins/awing.bmp'],
               'gun_offsets':[[9,-15],
                              [9,15]],
               'engine_offsets':[[-20,-8],
                                 [-20,8]]}

# create meta data for xwing skin
skins_meta_data['xwing'] = {'image_paths':['./graphics/sprite_skins/xwing.bmp'],
               'gun_offsets':[[9,-18],
                              [9,18]],
               'engine_offsets':[[-20,-8],
                                 [-20,8]]}

# create meta data for tie fighter skin
skins_meta_data['tiefighter'] = {'image_paths':['./graphics/sprite_skins/tiefighter.bmp'],
               'gun_offsets':[[9,-2],
                              [9,3]],
               'engine_offsets':[[-11,0]]}

# create meta data for hornet skin
skins_meta_data['hornet'] = {'image_paths':['./graphics/sprite_skins/hornet.bmp'],
               'gun_offsets':[[6,-2],
                              [6,3]],
               'engine_offsets':[[-20,0]]}

# create meta data for f35 skin
skins_meta_data['f35'] = {'image_paths':['./graphics/sprite_skins/f35.bmp'],
               'gun_offsets':[[6,-2],
                              [6,3]],
               'engine_offsets':[[-17,0]]}

# create meta data for red laser beam skin
skins_meta_data['red'] = {'image_paths':['./graphics/sprite_skins/redlaser.bmp']}

# create meta data for green laser beam skin
skins_meta_data['green'] = {'image_paths':['./graphics/sprite_skins/greenlaser.bmp']}

with open('sprite_skins_meta_data.yaml','w') as skins_meta_data_file:
    yaml.dump(skins_meta_data,skins_meta_data_file)
