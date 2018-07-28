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
                                #'sound':'./sounds/slinky_laser.wav',
                                #'sound':'./sounds/diy_missile_1.wav',
                                'spi':0.02}

# create meta data for green laser muzzle flash animation
animations_meta_data['green'] = {'image_paths':['./graphics/green_muzzle_flash/green_muzzle_flash' + str(i+1) + '.bmp' for i in range(6)],
                                #'sound':'./sounds/missile.wav',
                                'sound':'./sounds/slinky_laser.wav',
                                #'sound':'./sounds/diy_missile_1.wav',
                                'spi':0.02}

# create meta data for ship frames
animations_meta_data['ship_frame'] = {'red':{'image_paths':['./graphics/misc/hostile_frame.bmp']},
                    'green':{'image_paths':['./graphics/misc/ally_frame.bmp']},
                    'yellow':{'image_paths':['./graphics/misc/player_frame.bmp']}}

# create meta data for explosion animation
animations_meta_data['explosion'] = {'image_paths':['./graphics/explosion/explosion' + str(i+1) + '.bmp' for i in range(9)],
                                    #'sound':'./sounds/explosion.wav',
                                    'sound':'./sounds/blastwave_safe.wav',
                                    'spi':0.1}

# create meta data for hit animation
animations_meta_data['hit'] = {'sound':'./sounds/explosion.wav',
                                'spi':0.04}

# create meta data for engine flames
animations_meta_data['engine'] = {'image_paths':['./graphics/engine_flame/engine_flame' + str(i+1) + '.bmp' for i in range(4)],
                                    'spi':0.1}

# create meta data for rebel pilot images
animations_meta_data['rebel_pilot'] = {'image_paths':['./graphics/cockpit/rebel_pilot1.bmp',
                                                        './graphics/cockpit/skull.bmp']}
                                                        #'./graphics/cockpit/skull2.bmp']}

# create meta data for empire pilot images
animations_meta_data['empire_pilot'] = {'image_paths':['./graphics/cockpit/empire_pilot12.bmp',
                                                        './graphics/cockpit/skull.bmp']}
                                                        #'./graphics/cockpit/skull2.bmp']}

with open('animations_meta_data.yaml','w') as animations_meta_data_file:
    yaml.dump(animations_meta_data,animations_meta_data_file)
    
#----------------------------------------------
# [2] Create and save sprite skin meta data
#----------------------------------------------

skins_meta_data = {}

# create meta data for snowspeeder skin
skins_meta_data['snowspeeder'] = {'image_paths':['./graphics/sprite_skins/snowspeeder.bmp'],
               'gun_offsets':[[22,-11],
                              [22,11]],
               'engine_offsets':[[-22,-5],
                                 [-22,5]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for awing skin
skins_meta_data['awing'] = {'image_paths':['./graphics/sprite_skins/awing.bmp'],
               'gun_offsets':[[9,-15],
                              [9,15]],
               'engine_offsets':[[-20,-7],
                                 [-20,7]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for xwing skin
skins_meta_data['xwing'] = {'image_paths':['./graphics/sprite_skins/xwing.bmp'],
               'gun_offsets':[[13,-18],
                              [13,18],
                              [14,-16],
                              [14,16]],
               'engine_offsets':[[-25,-6],
                                 [-25,6]],
                'fire_modes':[[[0,1,2,3]],
                              [[0,1],
                               [2,3]], # coupled
                              [[0], #singe
                               [1],
                               [2],
                               [3]]]}

# create meta data for tie fighter skin
skins_meta_data['tiefighter'] = {'image_paths':['./graphics/sprite_skins/tiefighter.bmp'],
               'gun_offsets':[[9,-2],
                              [9,3]],
               'engine_offsets':[[-11,0]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for the tie interceptor skin                
skins_meta_data['tieinterceptor'] = {'image_paths':['./graphics/sprite_skins/tieinterceptor.bmp'],
               'gun_offsets':[[20,-17],
                              [20,17],
                              [20,-13],
                              [20,13]],
               'engine_offsets':[[-18,0]],
                'fire_modes':[[[0,1,2,3]], # all
                              [[0,1],
                               [2,3]], # coupled
                              [[0], #singe
                               [1],
                               [2],
                               [3]]]}

# create meta data for vader's tie fighter
skins_meta_data['tievader'] = {'image_paths':['./graphics/sprite_skins/tievader.bmp'],
               'gun_offsets':[[18,-9],
                              [18,9]],
               'engine_offsets':[[-18,-3],
                                 [-18,3]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for hornet skin
skins_meta_data['hornet'] = {'image_paths':['./graphics/sprite_skins/hornet.bmp'],
               'gun_offsets':[[6,-2],
                              [6,3]],
               'engine_offsets':[[-20,0]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for f35 skin
skins_meta_data['f35'] = {'image_paths':['./graphics/sprite_skins/f35.bmp'],
               'gun_offsets':[[6,-2],
                              [6,3]],
               'engine_offsets':[[-17,0]],
                'fire_modes':[[[0,1]], # coupled
                              [[0], #singe
                               [1]]]}

# create meta data for red laser beam skin
skins_meta_data['red'] = {'image_paths':['./graphics/sprite_skins/redlaser.bmp']}

# create meta data for green laser beam skin
skins_meta_data['green'] = {'image_paths':['./graphics/sprite_skins/greenlaser.bmp']}

with open('sprite_skins_meta_data.yaml','w') as skins_meta_data_file:
    yaml.dump(skins_meta_data,skins_meta_data_file)


#----------------------------------------------
# [3] Create and save the per-level meta data
#----------------------------------------------
    
level_template_meta_data = {}

level_template_meta_data['music'] = {'sound':'./sounds/platformer2.wav',
                                    'volume':1}
    
level_template_meta_data['player'] = {'ship_init_kwargs':{'center':[1400,350],
                                                          'angle':180,
                                                          'speed':200,
                                                          'd_angle_degrees_per_second':150,
                                                          'd_speed_pixel_per_second':20,
                                                          'max_speed_pixel_per_second':250},
                                        'ship':'awing',
                                        'laser':'red'}

level_template_meta_data['ally'] = {'ship_init_kwargs':{'center':[(1400,100),
                                                                    (1400,700)],
                                                        'angle':[180,
                                                                180],
                                                        'speed':[250,
                                                                250],
                                                        'd_angle_degrees_per_second':[100,
                                                                                       100],
                                                        'd_speed_pixel_per_second':[20,
                                                                                     20],
                                                        'max_speed_pixel_per_second':[250,
                                                                                     250]},
                                    'ship':'awing',
                                    'laser':'red'}

level_template_meta_data['hostile'] = {'ship_init_kwargs':{'center':((50,100),
                                                                       (50,350),
                                                                       (50,700)),
                                                            'angle':[0,
                                                                      0,
                                                                      0],
                                                            'speed':[250,
                                                                      250,
                                                                      250],
                                                            'd_angle_degrees_per_second':[100,
                                                                                           100,
                                                                                           100],
                                                            'd_speed_pixel_per_second':[20,
                                                                                         20,
                                                                                         20],
                                                            'max_speed_pixel_per_second':[250,
                                                                                           250,
                                                                                           250]},
                                        'ship':'tiefighter',
                                        'laser':'green'}

game_level_meta_data = [level_template_meta_data ] * 5

with open('game_level_meta_data.yaml','w') as game_level_data_file:
    yaml.dump(game_level_meta_data,game_level_data_file)
