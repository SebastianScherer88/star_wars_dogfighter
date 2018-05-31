# -*- coding: utf-8 -*-
"""
Created on Thu May 31 22:28:20 2018

@author: bettmensch
"""

import yaml
import numpy

with open('sprite_meta_data.yaml','r') as meta_file:
    meta_data = yaml.load(meta_file)


cannon_tips_rel_to_centers = {}

for ship_type in meta_data.keys():
    cannon_tips = meta_data[ship_type]['cannon_tip_positions']
    cannon_tips_rel_to_centers[ship_type] = cannon_tips - numpy.array([20,20])
    
for ship_type in cannon_tips_rel_to_centers.keys():
    meta_data[ship_type]['cannon_tip_positions'] = cannon_tips_rel_to_centers[ship_type]
    
with open('sprite_meta_data.yaml','w') as meta_file:
    yaml.dump(meta_data,meta_file)
