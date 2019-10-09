# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 20:15:48 2018

@author: bettmensch
"""

import cx_Freeze
import os

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

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
                           "include_files":["./lib/",
                                            "./graphics/",
                                            "./sounds/",
                                            "./meta/",
                                            (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),'./lib/tcl86t.dll'),
                                            (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),'./lib/tk86t.dll')]}},
    executables = executables

    )