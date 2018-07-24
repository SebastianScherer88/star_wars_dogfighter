# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 19:37:28 2018

@author: bettmensch
"""

# [0]
def main():
    
    import pygame as pg
    import os
    import sys
    
    os.chdir("C:\\Users\\bettmensch\\GitReps\\star_wars_dogfighter")
    pg.init()
    size = (1500,700)
    main_screen = pg.display.set_mode((size))
    
    # [1] load images
    
    WHITE = (255,255,255)
    
    #load cockpit image and set colorkey
    cockpit_image = pg.image.load("./graphics/cockpit/cockpit3.bmp")
    cockpit_image.set_colorkey(WHITE)
    
    # load background image
    background_image = pg.image.load("./graphics/misc/star_wars_background_24bit.bmp")
    
    # load rebel pilot image
    rebel_pilot = pg.image.load("./graphics/cockpit/rebel_pilot1.bmp")
    
    # load empire pilot image
    empire_pilot = pg.image.load("./graphics/cockpit/empire_pilot1.bmp")
    
    # load tie fighte image
    tie_fighter = pg.image.load("./graphics/sprite_skins/tiefighter.bmp")
    tie_fighter.set_colorkey((255,255,255))
    
    # load xwing fighter image
    xwing = pg.image.load("./graphics/sprite_skins/xwing.bmp")
    xwing.set_colorkey((255,255,255))
    
    # load hostile frame
    hostile_frame = pg.image.load("./graphics/misc/hostile_frame.bmp")
    hostile_frame.set_colorkey((255,255,255))
    
    # [2] blit cockpit and background
    
    # background
    main_screen.blit(background_image, (0,0))
    
    # cockpit frame
    main_screen.blit(cockpit_image, (0,0))
    
    # [3] left/right side titles
    
    # get a font and text color
    title_font = pg.font.Font('freesansbold.ttf',25)
    TEXT_COLOR = (0,65,65)
    
    # render title for left cockpit side
    squadron_title = title_font.render("Squadron",False,TEXT_COLOR)
    
    # render title for right cockpit side
    target_pc_title = title_font.render("Target Computer",False,TEXT_COLOR)
    
    # put up squadron title below
    main_screen.blit(squadron_title, (200,300))
    
    # put up target pc title above
    main_screen.blit(target_pc_title, (200,50))
    
    # [4] Ally displays
    
    # define function that creates an ally pilot display
    def get_ally_display(**kwargs): # (left,top)
        
        # get colored display surface
        display_canvas = pg.Surface(kwargs['display_size'])
        display_canvas.fill(kwargs['display_color'])
        
        # get pilot image and blit to surface
        display_canvas.blit(kwargs['pilot_image'],(kwargs['pilot_image_offsets']))
        
        # get colored pilot health bar and blit to display canvas
        ally_health_bar = pg.Surface(kwargs['health_bar_size'])
        ally_health_bar.fill(kwargs['health_bar_color'])
        display_canvas.blit(ally_health_bar,kwargs['health_bar_offsets'])
        
        # get colored ally name and blit to display canvas
        stats_name_font = pg.font.Font("freesansbold.ttf",kwargs['stats_name_font_size'])
        ally_name = stats_name_font.render(kwargs['ship_name'],
                                           False,
                                           kwargs['display_text_color'])
        display_canvas.blit(ally_name,(kwargs['ally_name_offsets']))
        
        # get colored ally target name and blit to display on canvas
        ally_target_name = stats_name_font.render("Target:",
                                                  False,
                                                  kwargs['display_text_color'])
        display_canvas.blit(ally_target_name,(kwargs['ally_target_name_offsets']))
        
        # get colored ally target image, add target image and id and blit to display
        ally_target_canvas = pg.Surface(kwargs['ally_target_canvas_size'])
        ally_target_canvas.fill(kwargs['ally_target_canvas_color'])
        ally_target_canvas.blit(kwargs['target_sprite_image'],(30,30))
        ally_target_canvas.blit(hostile_frame,(25,25))
        target_id_font = pg.font.Font("freesansbold.ttf",kwargs['ally_target_id_font_size'])
        target_id = target_id_font.render(kwargs['ally_target_id'],
                                          False,
                                          kwargs['ally_target_id_font_color'])
        ally_target_canvas.blit(target_id,(25,75))
        display_canvas.blit(ally_target_canvas,(kwargs['ally_target_image_offsets']))
        
        
        return display_canvas
    
    # define some constants
    ALLY_IMAGE = rebel_pilot
    HOSTILE_IMAGE = empire_pilot
    DISPLAY_SIZE = (250,150)
    DISPLAY_COLOR = (0,65,65)
    DISPLAY_TEXT_COLOR = (200,200,200)
    HEALTH_BAR_COLOR = (0,100,100)
    PILOT_IMAGE_OFFSETS = (30,40)
    HEALTH_BAR_SIZE = (10,40)
    HEALTH_BAR_OFFSETS = (10,100)  
    STATS_NAME_FONT_SIZE = 20
    ALLY_NAME_OFFSETS = (30,10)
    ALLY_TARGET_NAME_OFFSETS = (140,10)
    ALLY_TARGET_CANVAS_SIZE = (100,100)
    ALLY_TARGET_CANVAS_COLOR = (0,0,0)
    ALLY_TARGET_IMAGE_OFFSETS = (140, 40)
    ALLY_TARGET_ID_FONT_SIZE = 12
    ALLY_TARGET_ID_FONT_COLOR = (255,255,255)
    
    # define list of parameter dictionaries
    params1 = {'pilot_image':rebel_pilot,
               'target_sprite_image':tie_fighter,
                'ship_name':"Ally 1",
               'ally_hit_points':20,
               'ally_target_id':"Hostile 2",
               'display_size':DISPLAY_SIZE,
               'display_color':DISPLAY_COLOR,
               'display_text_color':DISPLAY_TEXT_COLOR,
               'health_bar_color':(0,200,0),
               'pilot_image_offsets':PILOT_IMAGE_OFFSETS,
               'health_bar_size': (10,70),
               'health_bar_offsets':(10,70),
               'stats_name_font_size':STATS_NAME_FONT_SIZE,
               'ally_name_offsets':ALLY_NAME_OFFSETS,
               'ally_target_name_offsets':ALLY_TARGET_NAME_OFFSETS,
               'ally_target_canvas_size':ALLY_TARGET_CANVAS_SIZE,
               'ally_target_canvas_color':ALLY_TARGET_CANVAS_COLOR,
               'ally_target_image_offsets':ALLY_TARGET_IMAGE_OFFSETS,
               'ally_target_id_font_size':ALLY_TARGET_ID_FONT_SIZE,
               'ally_target_id_font_color':ALLY_TARGET_ID_FONT_COLOR}
    
    params2 = {'pilot_image':rebel_pilot,
               'target_sprite_image':tie_fighter,
                'ship_name':"Ally 3",
               'ally_hit_points':20,
               'ally_target_id':"Hostile 3",
               'display_size':DISPLAY_SIZE,
               'display_color':DISPLAY_COLOR,
               'display_text_color':DISPLAY_TEXT_COLOR,
               'health_bar_color':(200,0,0),
               'pilot_image_offsets':PILOT_IMAGE_OFFSETS,
               'health_bar_size': (10,20),
               'health_bar_offsets':(10,120),
               'stats_name_font_size':STATS_NAME_FONT_SIZE,
               'ally_name_offsets':ALLY_NAME_OFFSETS,
               'ally_target_name_offsets':ALLY_TARGET_NAME_OFFSETS,
               'ally_target_canvas_size':ALLY_TARGET_CANVAS_SIZE,
               'ally_target_canvas_color':ALLY_TARGET_CANVAS_COLOR,
               'ally_target_image_offsets':ALLY_TARGET_IMAGE_OFFSETS,
               'ally_target_id_font_size':ALLY_TARGET_ID_FONT_SIZE,
               'ally_target_id_font_color':ALLY_TARGET_ID_FONT_COLOR}
    
    
    # get display of first two allies
    first_ally_display = get_ally_display(**params1)
    second_ally_display = get_ally_display(**params2)
        
    # blit display of first ally
    main_screen.blit(first_ally_display,(20,350))
    main_screen.blit(second_ally_display,(290,350))
    
    # get params for target computer display
    params3 = {'pilot_image':empire_pilot,
               'target_sprite_image':xwing,
                'ship_name':"Hostile 3",
               'ally_hit_points':20,
               'ally_target_id':"Ally 1",
               'display_size':DISPLAY_SIZE,
               'display_color':DISPLAY_COLOR,
               'display_text_color':DISPLAY_TEXT_COLOR,
               'health_bar_color':(200,0,0),
               'pilot_image_offsets':PILOT_IMAGE_OFFSETS,
               'health_bar_size': (10,20),
               'health_bar_offsets':(10,120),
               'stats_name_font_size':STATS_NAME_FONT_SIZE,
               'ally_name_offsets':ALLY_NAME_OFFSETS,
               'ally_target_name_offsets':ALLY_TARGET_NAME_OFFSETS,
               'ally_target_canvas_size':ALLY_TARGET_CANVAS_SIZE,
               'ally_target_canvas_color':ALLY_TARGET_CANVAS_COLOR,
               'ally_target_image_offsets':ALLY_TARGET_IMAGE_OFFSETS,
               'ally_target_id_font_size':ALLY_TARGET_ID_FONT_SIZE,
               'ally_target_id_font_color':ALLY_TARGET_ID_FONT_COLOR}
    
    # get target computer display
    main_target = get_ally_display(**params3)
    
    # blit target computer display
    main_screen.blit(main_target,(150,100))
    
    
    # [-2] flip
    pg.display.flip()
    
    # [-1] exit
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:                    
                pg.quit()
                sys.exit()
                
main()