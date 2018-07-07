# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 20:15:48 2018

@author: bettmensch
"""

import cx_Freeze
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tk8.6'

executables = [cx_Freeze.Executable(script = "./lib/game_class.py")]

cx_Freeze.setup(
    name="Star Wars Dogfighter",
    options={"build_exe": {"packages":["pygame",
                                       "numpy",
					"numpy.lib.format",
                                       "math",
                                       "yaml",
                                       "sys",
                                       "os",
                                       "random"],
                           "include_files":["./lib/animation_classes.py",
                                            "./lib/basic_sprite_class.py",
                                            "./lib/sprite_classes.py",
                                            "./lib/weapons_classes.py",
                                            "./graphics/sprite_skins/xwing.bmp",
                                            "./graphics/sprite_skins/awing.bmp",
                                            "./graphics/sprite_skins/tieinterceptor.bmp",
                                            "./graphics/sprite_skins/tiefighter.bmp",
                                            "./graphics/sprite_skins/redlaser.bmp",
                                            "./graphics/sprite_skins/greenlaser.bmp",
                                            "./graphics/engine_flame/engine_flame1.bmp",
                                            "./graphics/engine_flame/engine_flame2.bmp",
                                            "./graphics/engine_flame/engine_flame3.bmp",
                                            "./graphics/engine_flame/engine_flame4.bmp",
                                            "./graphics/explosion/explosion1.bmp",
                                            "./graphics/explosion/explosion2.bmp",
                                            "./graphics/explosion/explosion3.bmp",
                                            "./graphics/explosion/explosion4.bmp",
                                            "./graphics/explosion/explosion5.bmp",
                                            "./graphics/explosion/explosion6.bmp",
                                            "./graphics/explosion/explosion7.bmp",
                                            "./graphics/explosion/explosion8.bmp",
                                            "./graphics/explosion/explosion9.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash1.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash2.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash3.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash4.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash5.bmp",
                                            "./graphics/green_muzzle_flash/green_muzzle_flash6.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash1.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash2.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash3.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash4.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash5.bmp",
                                            "./graphics/red_muzzle_flash/red_muzzle_flash6.bmp",
                                            "./graphics/misc/ally_frame.bmp",
                                            "./graphics/misc/hostile_frame.bmp",
                                            "./graphics/misc/player_frame.bmp",
                                            "./graphics/misc/star_wars_background.bmp",
                                            "./graphics/misc/star_wars_background_24bit.bmp",
                                            "./sounds/explosion.wav",
                                            "./sounds/explosion.wav",
                                            "./meta/animations_meta_data.yaml",
                                            "./meta/sprite_skins_meta_data.yaml"]}},
    executables = executables

    )