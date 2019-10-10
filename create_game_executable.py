# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 20:15:48 2018

@author: bettmensch
"""

import cx_Freeze
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tk8.6'

executables = [cx_Freeze.Executable(script = "./lib/star_wars_dogfighter.py")]

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
                           "include_files":["./lib/",
                                            "./graphics/",
                                            "./sounds/",
                                            "./meta/"]}},
    executables = executables

    )