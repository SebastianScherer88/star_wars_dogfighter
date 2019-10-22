# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 20:15:48 2018

@author: bettmensch
"""

import cx_Freeze
import os

os.environ['TCL_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\bettmensch\Anaconda3\envs\game_env\tcl\tk8.6'

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
mkl_dll_location = os.path.join(PYTHON_INSTALL_DIR,'Library','bin')
mkl_dll_files = os.listdir(mkl_dll_location)

mkl_files_to_include = [dll_file_name for dll_file_name in mkl_dll_files if dll_file_name.startswith('mkl_')]
mkl_files_to_incldue = [dll_file_name for dll_file_name in mkl_files_to_include if dll_file_name.endswith('.dll')]


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
                                            "./meta/",
                                            # lib*.dll file
                                            os.path.join(mkl_dll_location,'libiomp5md.dll')] +
                                            # mkl*.dll files
                                            [os.path.join(mkl_dll_location,mkl_file) for mkl_file in mkl_files_to_include]}},
    executables = executables

    )