# -*- coding: utf-8 -*-
"""
Created on Thu May 31 22:28:20 2018

@author: bettmensch
"""

import yaml
import numpy
import os

os.chdir('C:/Users/bettmensch/GitReps/star_wars_dogfighter/meta')

with open('sprite_meta_data.yaml','r') as meta_file:
    meta_data = yaml.load(meta_file)

all_image_paths = {}

for ship_type in meta_data.keys():
    image_paths = [meta_data[ship_type]['image_path'],]
    del meta_data[ship_type]['image_path']
    all_image_paths[ship_type] = image_paths
    
for ship_type in all_image_paths.keys():
    meta_data[ship_type]['image_paths'] = all_image_paths[ship_type]
    
with open('sprite_meta_data.yaml','w') as meta_file:
    yaml.dump(meta_data,meta_file)
