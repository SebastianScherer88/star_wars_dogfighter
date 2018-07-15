# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:09:47 2018

@author: Atreju Maischberger
"""

# demo gam states here
import sys
import os
import yaml
import time

import pygame as pg
import numpy as np

from pygame.sprite import Group, collide_mask, groupcollide
from basic_sprite_classes import BasicSprite
from sprite_classes import ShipSprite, AIShipSprite, ShipBio
from animation_classes import BasicAnimation,TrackingAnimation

class Game(object):
    
    def __init__(self,
                 screen_width=1500,
                 screen_height=700,
                 fps=30,
                 background_image = None):
        '''Initializes the game object and also the game'''
        
        # initialize pygame (handles pretty much eveything)
        pg.init()
        
        # create clock    
        self.clock = pg.time.Clock()
        
        # background
        self.background_image = pg.image.load('./graphics/misc/star_wars_background_24bit.bmp')
        
        # cockpit frame
        self.cockpit_frame = pg.image.load('./graphics/cockpit/cockpit_test.bmp')
        self.cockpit_frame.set_colorkey((255,255,255))
        
        self.fps = fps
        
        # initialize main screen
        size = screen_width, screen_height # set screen size
        self.screen = pg.display.set_mode(size)
        pg.display.set_caption("STAR WARS DOGFIGHTER")
        
        # load meta data
        with open('./meta/sprite_skins_meta_data.yaml','r') as skins_meta_file:
            self.skins_meta_data = yaml.load(skins_meta_file)
        
        with open('./meta/animations_meta_data.yaml','r') as animations_meta_file:
            self.animations_meta_data = yaml.load(animations_meta_file)
            
        with open ('./meta/game_level_meta_data.yaml','r') as level_meta_file:
            self.level_meta_data = yaml.load(level_meta_file)
        
        # start start-up animation and welcome screen
        player_feedback = self.welcome_screen()
        
        # if player hasnt closed the pygame window, process to level 1 of game
        if player_feedback == 'pass':
            
            # start levels
            level_index = 0
            
            while level_index < 5:
                # get level specs for i-th level
                level_specs = self.level_meta_data[level_index]
                
                # get meta data for i-th level
                level_meta_data = self._collect_meta_data_for_level(level_index,
                                                                    level_specs)
                
                # start level and receive level outcome
                player_feedback, level_outcome = self.start_level(level_meta_data)
                
                if player_feedback == 'quit_game':
                    break 
                elif player_feedback == 'retry':
                    # repeat level = repeat loop with unchanged index
                    pass
                elif level_outcome == 'pass':
                    # increase level index by one
                    level_index += 1
            
        # display game over message
        self.goodbye_screen()
        
        # quit (py)game
        pg.quit()
        sys.exit()
        
    def handle_startup_events_queue(self,
                                    player_input):
        '''Util function that produces returns a break flag when user pressing
        the escape key. Can be used for events handling during game start up animation
        in the future and welcome screen display.'''
        
        events = pg.event.get()
        
        for event in events:
            # if player wants to quit, record that feedback
            if event.type == pg.QUIT:                    
                # quit this level
                player_input = 'quit_game'
            # if player wants to skip/continue to game, record that feedback
            if event.type == pg.KEYDOWN:
                player_input = 'pass'
                
        return player_input
    
    def _get_surface_from_text(self,
                               message = '',
                               font = 'freesansbold.ttf',
                               size = 40,
                               text_color = (255,0,0),
                               background_color = None):
        '''Util function that generates a pygame surface (transparent unless 
        background_color is specified) by rendering the specified
        text message according to the passed specs.'''
        
        # get font from specs
        font = pg.font.Font(font,size)
        
        # render text to get surface
        text_surface = font.render(message,False,text_color,background_color)
        
        return text_surface
    
    def blit_message_and_wait(self,
                             main_message,
                             sub_message=None,
                             main_size = 40,
                             sub_size = 20,
                             font = 'freesansbold.ttf',
                             text_color = (255, 0, 0),
                             background_color = None,
                             blackout = True,
                             wait_seconds = 0,
                             blit_mode=True,
                             text_groups=None):
        '''Util message that can be used to blit a message with smaller submessage
        to the center of the main screen, and wait a bit. If blit_mode is set to True,
        messages will be blitted straight to the screen. Otherwise, a pair of BasicSprites
        with rendered text surfaces will be added to the passed sprite_groups list 
        of groups.'''
        
        # black out screen if needed
        if blackout:
            self.screen.fill((0,0,0))
            
        # get positions for main and sub message
        center = self.screen.get_rect().center
        sub_center = center[0], center[1] + main_size
            
        # render, position and blit main and sub message
        for text,pos,size in zip([main_message,sub_message],
                            [center,sub_center],
                            [main_size, sub_size]):
            if text != None:
                text_surface = self._get_surface_from_text(text,
                                                           font,
                                                           size,
                                                           text_color,
                                                           background_color)
                text_rect = text_surface.get_rect()
                text_rect.center = pos
                if blit_mode:
                    self.screen.blit(text_surface,text_rect)
                else:
                    BasicSprite(self.fps,
                                self.screen,
                                [text_surface],
                                text_groups,
                                center = pos,
                                is_transparent = False)
                
        # display drawings if in blit mode
        if blit_mode:
            pg.display.flip()
        
        # wait if needed
        if wait_seconds:
            pg.time.wait(int(wait_seconds * 1000))
        
    def welcome_screen(self):
        '''Util function that start any potential animations when starting up the 
        game and prints the game name with "Press any key to continue" message.'''
        
        player_input = ''
        
        # get sprite group for screen messages
        start_up_sprites = Group()
        
        # get clock
        clock = pg.time.Clock()
        
        # add STAR WARS DOGFIGHTER text sprite to group/main screen
        self.blit_message_and_wait("STAR WARS DOGFIGHTER",
                                   blackout = False,
                                   blit_mode=False,
                                   text_groups=[start_up_sprites])
                
        # create "press any key to continue to game" animation
        continue_surfaces = [self._get_surface_from_text(message,size=20) for message in ("Press any key to continue", "")]
        
        # get rectange of main screen for positioning text messages
        center_x, center_y = self.screen.get_rect().center
        
        BasicAnimation(self.fps,
                       self.screen,
                       continue_surfaces,
                       1,
                       [start_up_sprites],
                       center = [center_x,center_y+200],
                       is_transparent = True,
                       looping = True)
        
        # start main game loop
        while True:
            # handle player pressing any key
            player_input = self.handle_startup_events_queue(player_input)
            
            # stop this segment if player wants to skip ahead to game
            if player_input in  ['pass','quit_game']:
                break
            
            # update message sprites
            start_up_sprites.update()
            
            # draw messae sprites
            self.screen.fill((0,0,0))
            start_up_sprites.draw(self.screen)
            pg.display.flip()
            
            # control speed up frame updates
            clock.tick(self.fps)
            
        return player_input
    
    def goodbye_screen(self):
        '''Util function that blits some game over type of message to screen,
        waits a bit and returns.'''
        
        self.blit_message_and_wait("GAME OVER",
                                   sub_message="Thank You For Playing!",
                                   wait_seconds = 1.5)
            
    def _collect_meta_data_for_level(self,
                                     level_index,
                                     level_specs):
        '''Util function that collects all the sprite related meta data for player,
        allies and hostiles for current level.
        Input argument is
        - level_specs: dictionary. Contains the keys
            - 'level_index': integer
            - 'player': dictionary
            - 'ally': dictionary
            - 'hostile': dictionary
        with info specifying ship type, laser color and initial values for sprite
        initializers in via the sub keys 'ship', 'laser' and 'ship_init_kwargs',
        respectively.'''
        
        # get ship and laser specs for player, allies and hostiles for this level
        player_ship, player_laser = level_specs['player']['ship'],level_specs['player']['laser']
        ally_ship, ally_laser = level_specs['ally']['ship'],level_specs['ally']['laser']
        hostile_ship, hostile_laser = level_specs['hostile']['ship'],level_specs['hostile']['laser']

        # assign sides to player to get pilot images
        if player_ship in ['awing','xwing','ywing']:
            player_side = 'rebel'
            hostile_side = 'empire'
        else:
            player_side = 'empire'
            hostile_side = 'rebel'

        # pilot skins
        pilot_images = {'player':[pg.image.load(image_path) for image_path in self.animations_meta_data[player_side+'_pilot']['image_paths']],
                        'ally': [pg.image.load(image_path) for image_path in self.animations_meta_data[player_side+'_pilot']['image_paths']],
                        'hostile': [pg.image.load(image_path) for image_path in self.animations_meta_data[hostile_side+'_pilot']['image_paths']]}
        
        
        
        # ship skins
        ship_images = {'player':[pg.image.load(image_path) for image_path in self.skins_meta_data[player_ship]['image_paths']],
                            'ally':[pg.image.load(image_path) for image_path in self.skins_meta_data[ally_ship]['image_paths']],
                            'hostile':[pg.image.load(image_path) for image_path in self.skins_meta_data[hostile_ship]['image_paths']]}
        
        # gun offsets
        gun_offsets = {'player':np.array(self.skins_meta_data[player_ship]['gun_offsets']).astype('float'),
                       'ally':np.array(self.skins_meta_data[ally_ship]['gun_offsets']).astype('float'),
                       'hostile':np.array(self.skins_meta_data[hostile_ship]['gun_offsets']).astype('float')}
        
        # engine offsets
        engine_offsets = {'player':np.array(self.skins_meta_data[player_ship]['engine_offsets']).astype('float'),
                          'ally':np.array(self.skins_meta_data[ally_ship]['engine_offsets']).astype('float'),
                          'hostile':np.array(self.skins_meta_data[hostile_ship]['engine_offsets']).astype('float')}
        
        # fire modes
        fire_modes = {'player':self.skins_meta_data[player_ship]['fire_modes'],
                      'ally':self.skins_meta_data[ally_ship]['fire_modes'],
                      'hostile':self.skins_meta_data[hostile_ship]['fire_modes']}
        
        # laser images
        laser_images = {'player':[pg.image.load(image_path) for image_path in self.skins_meta_data[player_laser]['image_paths']],
                        'ally':[pg.image.load(image_path) for image_path in self.skins_meta_data[ally_laser]['image_paths']],
                        'hostile':[pg.image.load(image_path) for image_path in self.skins_meta_data[hostile_laser]['image_paths']]}
        
        # laser sounds
        laser_sounds = {'player':pg.mixer.Sound(self.animations_meta_data[player_laser]['sound']),
                        'ally':pg.mixer.Sound(self.animations_meta_data[ally_laser]['sound']),
                        'hostile':pg.mixer.Sound(self.animations_meta_data[hostile_laser]['sound'])}
        
        # muzzle images
        muzzle_flash_images = {'player':[pg.image.load(image_path) for image_path in self.animations_meta_data[player_laser]['image_paths']],
                                'ally':[pg.image.load(image_path) for image_path in self.animations_meta_data[ally_laser]['image_paths']],
                                'hostile':[pg.image.load(image_path) for image_path in self.animations_meta_data[hostile_laser]['image_paths']]}
        
        # muzzle seconds per image
        muzzle_flash_spi = {'player':self.animations_meta_data[player_laser]['spi'],
                             'ally':self.animations_meta_data[ally_laser]['spi'],
                             'hostile':self.animations_meta_data[hostile_laser]['spi']}
        
        # ship sprites' intial values
        ship_init_kwargs = {'player':level_specs['player']['ship_init_kwargs'],
                            'ally':level_specs['ally']['ship_init_kwargs'],
                            'hostile':level_specs['hostile']['ship_init_kwargs']}
        
        level_meta_data = {'ship_images':ship_images,
                          'gun_offsets':gun_offsets,
                          'engine_offsets':engine_offsets,
                          'fire_modes':fire_modes,
                          'laser_images':laser_images,
                          'laser_sounds':laser_sounds,
                          'muzzle_flash_images':muzzle_flash_images,
                          'muzzle_flash_spi':muzzle_flash_spi,
                          'explosion_images':[pg.image.load(image_path) for image_path in self.animations_meta_data['explosion']['image_paths']],
                          'explosion_sounds':pg.mixer.Sound(self.animations_meta_data['explosion']['sound']),
                          'explosion_spi':self.animations_meta_data['explosion']['spi'],
                          'engine_images':[pg.image.load(image_path) for image_path in self.animations_meta_data['engine']['image_paths']],
                          'engine_spi':self.animations_meta_data['engine']['spi'],
                          'piloting_cone_sine':0.1,
                          'gunning_cone_sine':0.1,
                          'ship_init_kwargs':ship_init_kwargs,
                          'level_number':level_index+1,
                          'pilot_images':pilot_images}
        
        return level_meta_data
    
    def _collect_sprite_groups_for_level(self):
        '''Util function that initializes and returns sprite groups for current level.'''
        
        # ship sprites will be added to these group
        ship_groups = {'any':Group(),
                       'ally':Group(),
                       'hostile':Group()}
        ship_groups['player'] = ship_groups['ally'] # allies are on player's side; only one ship group needed
        
        # projectile sprites/lasers will be added to these groups
        laser_beams_groups = {'ally':Group(),
                              'hostile':Group()}
        laser_beams_groups['player'] = laser_beams_groups['ally'] # allies are on player's side; only one laser group needed
        
        # animations and other non-collidable sprites will be added to this group
        non_collidables_group = {'any':Group()}
        
        # end of level messages will be added to this group
        level_endings = {'pass':Group(),
                         'fail':Group()}
        
        # add group for in-cockpit sprites
        cockpit_group = {'any':Group()}
        
        level_sprite_groups = {'ships':ship_groups,
                              'lasers':laser_beams_groups,
                              'non_colliders':non_collidables_group,
                              'level_endings':level_endings,
                              'cockpit':cockpit_group}
        
        return level_sprite_groups
    
    def _add_sprites_to_groups_for_level(self,
                               level_meta_data,
                               level_sprite_groups):
        '''Util function that spawns all the ships for current level. Returns the
        intitalized player ShipSprite object.'''
        # create player sprite and add to relevant groups / provide with relevant groups
        player = self.spawn_ship('player',
                                 0,
                                 level_meta_data,
                                 level_sprite_groups)
        
        # create allies for this level and add to groups
        self.spawn_squadron('ally',
                            level_meta_data,
                            level_sprite_groups)
        
        # create hostiles for this level and add to groups
        self.spawn_squadron('hostile',
                            level_meta_data,
                            level_sprite_groups)
        
        # render level ending messages and add to groups
        self.spawn_level_ending_messages(level_sprite_groups)
        
        return player
        
    def _toggle_pause(self,
                      level_status,
                      paused):
        '''Util function that toggles the pause mode during the game.'''
        
        # only pause and display pause message if level is ongoing
        if level_status == 'ongoing':
            # invert pause state
            paused = not paused
                            
            if paused:
                # display pause message on screen
                self.blit_message_and_wait("PAUSED",
                                           sub_message="Press [Esc]ape to continue, [Q] to quit or [R] to retry level",
                                           blackout = False)
                
        return paused
        
    def _toggle_sound(self,
                      level_sprite_groups,
                      sound):
        '''Util function that toggles the sound mode during the game.'''
        
        # invert sound state
        sound = not sound
                        
        # update sprites if needed
        for ship in level_sprite_groups['ships']['any'].sprites():
            ship._sound = sound
            
        return sound
    
    def handle_level_events_queue(self,
                            player_input,
                            level_status,
                            level_sprite_groups,
                            paused,
                            sound,
                            player):
        '''Handles the events in the pygame event queue. Changes game state
        variables as needed and returns their updated versions.'''
        
        for event in pg.event.get():
            if event.type == pg.QUIT:                    
                # quit this level
                player_input = 'quit_game'
                
            elif event.type == pg.KEYDOWN:
                
                # toggle pause state if needed
                if event.key == pg.K_ESCAPE:
                    paused = self._toggle_pause(level_status,
                                                paused)
                        
                # quit game if in pause mode or level has failed
                if event.key == pg.K_q:
                    if paused or level_status == 'fail':
                        # quit this level
                        player_input = 'quit_game'
                        
                # return to main game to retry level if level has failed
                if event.key == pg.K_r:
                    if paused or level_status == 'fail':
                        player_input = 'retry'
                    
                # toggle sound if needed
                if event.key == pg.K_s:
                    sound = self._toggle_sound(level_sprite_groups,
                                               sound)
                
                # control player fire mode
                if event.key == pg.K_f:
                    player._toggle_fire_mode()
                    
                # control player fire commands
                if event.key == pg.K_SPACE:
                    player._command_to_fire = True
                    
                # control player acceleration
                if event.key == pg.K_UP:
                    player._d_speed += player._d_speed_pixel_per_frame
                if event.key == pg.K_DOWN:
                    player._d_speed -= player._d_speed_pixel_per_frame
                    
                # control player steering
                if event.key == pg.K_RIGHT:
                    player._d_angle -= player._d_angle_degrees_per_frame
                if event.key == pg.K_LEFT:
                    player._d_angle += player._d_angle_degrees_per_frame
                    
            elif event.type == pg.KEYUP:
                
                # control player fire commands
                if event.key == pg.K_SPACE:
                    player._command_to_fire = False
                
                # control player acceleration
                if event.key == pg.K_UP:
                    player._d_speed -= player._d_speed_pixel_per_frame
                if event.key == pg.K_DOWN:
                    player._d_speed += player._d_speed_pixel_per_frame
                    
                # control player steering
                if event.key == pg.K_RIGHT:
                    player._d_angle += player._d_angle_degrees_per_frame
                if event.key == pg.K_LEFT:
                    player._d_angle -= player._d_angle_degrees_per_frame
                    
        return player_input, level_status, paused, sound
        
    def start_level(self,
                    level_meta_data):
        
        '''Kick starts a level with:
            - skins_meta_data: dictionary. Holds the 
            - level_number: interger. Specifies the level number, i.e. "Level 10"
            - player_data: dictionary. Contains the following keys/information:
                "ship": player ship type; specifies player ship sprite skin, i.e. "xwing"
                "laser": player laser type; either "red" or "green"
                "center":  numpy array, specifying the initial starting position of player
                "angle": integer, specifying the initial orientation of player; 
                        angle is counted-clockwise, where 0 degrees points along positive x-axis
                "speed": integer, specifying initial speed of player (in pixel per second)
                "d_angle_degrees_per_second": float, specifying the turning rate of the player (in degrees persecond)
                "d_speed_pixel_per_second": float, specifying the accelration of player (in pixel per second squared)
                "max_speed_pixel_per_second":  float, specifying the player's top speed (in pixel per seconds)
            - ally_data: dictionary. Contains the following keys/information:
                "ship": ally ship type; specifies ally ships sprite skin, i.e. "xwing"
                "laser": ally laser type; either "red" or "green"
                "centers": a list containing one numpy array, specifying the initial starting position of allies
                "angles": a list containing integers, specifying the initial orientation of allies; 
                        angle is counted-clockwise, where 0 degrees points along positive x-axis
                "speeds": a list containing integers, specifying initial speeds of allies (in pixel per second)
                "d_angle_degrees_per_seconds": a list containing floats, specifying the turning rate of the allies (in degrees persecond)
                "d_speed_pixel_per_seconds": a list containing floats, specifying the accelration of allies (in pixel per second squared)
                "max_speed_pixel_per_seconds": a list containing floats, specifying the allies's top speed (in pixel per seconds)
            - hostile_data: dictionary. See "ally_data" above.
        '''
        
        # get sprite groups for this level
        level_sprite_groups = self._collect_sprite_groups_for_level()
        
        # print level title to screen
        level_title = "LEVEL " + str(level_meta_data['level_number'])
        self.blit_message_and_wait(level_title,
                                   main_size = 40,
                                   wait_seconds = 1.5)
        
        # add sprites to groups for this level
        player = self._add_sprites_to_groups_for_level(level_meta_data,
                                                       level_sprite_groups)
        
        # sync player controls with current keyboard status before entering event loop
        self._sync_player_(player)
        
        # initialize pause, sound and next level countdown state variables
        player_input, paused, sound, t_pass, level_status = None, False, False, False, 'ongoing'
        
        # start main game loop
        while True:
            # handle events
            player_input, level_status, paused, sound = self.handle_level_events_queue(player_input,
                                                                                 level_status,
                                                                                 level_sprite_groups,
                                                                                 paused,
                                                                                 sound,
                                                                                 player)
                
            if not paused:
                # update game state
                self.update_game_state(level_sprite_groups)
                
                # draw update game state to screen
                self.draw_game_state(level_sprite_groups,
                                     level_status)
                
                # check and handle collisions
                self.handle_collisions(level_sprite_groups)
            
            # check if level done based on key events; if 'quit_game', quit level,
            # return to main game and quit
            if player_input in ['quit_game','retry']:
                break

            # check if level done based on game state
            level_status = self._get_level_status(level_sprite_groups)
            
            # start countdown (but only once!) before moving on to next level
            if level_status == 'pass' and t_pass == False:
                t_pass = time.time()
            elif level_status == 'pass':
                if time.time() - t_pass > 3:
                    break

            # control pace
            self.clock.tick(self.fps)
            
        return player_input, level_status
            
    def update_game_state(self,
                          sprite_groups):
        '''Updates the game state by updating all the game's sprite groups.'''
        
        sprite_groups['ships']['any'].update()
        sprite_groups['lasers']['ally'].update()
        sprite_groups['lasers']['hostile'].update()
        sprite_groups['non_colliders']['any'].update()
        sprite_groups['cockpit']['any'].update()
        #sprite_groups['level_endings']['any'].update()
        
    def draw_game_state(self,
                        sprite_groups,
                        level_status):
        '''Draws updated game state by wiping the game's main surface,
        drawing all the game's sprite groups and then flipping the game's main
        surface to display the drawings.'''
        
        # draw new game state    
        self.screen.blit(self.background_image,(0,0)) # paint over old game state
        
        sprite_groups['ships']['any'].draw(self.screen)
        sprite_groups['lasers']['ally'].draw(self.screen)
        sprite_groups['lasers']['hostile'].draw(self.screen)
        sprite_groups['non_colliders']['any'].draw(self.screen)
        
        if level_status == 'pass':
            sprite_groups['level_endings']['pass'].draw(self.screen)
        elif level_status == 'fail':
            sprite_groups['level_endings']['fail'].draw(self.screen)
            
        self.screen.blit(self.cockpit_frame,(0,0)) # paint over old cockpit frame
        
        # draw cockpit items
        sprite_groups['cockpit']['any'].draw(self.screen)
                   
        # flip canvas
        pg.display.flip()
        
    def handle_collisions(self,
                          sprite_groups):
        '''Checks for collisions between player sprite and enemy lasers, as well
        as enemy sprites and player lasers. Terminates any sprites that were
        shot down. Records the time of the kill.'''

        # check for enemy kills
        hit_allies = groupcollide(sprite_groups['ships']['ally'],
                                  sprite_groups['lasers']['hostile'],
                                      False,
                                      True,
                                      collide_mask)
        
        for hit_ally in hit_allies:
            # update hit ship's hit points attribute
            hit_ally._hit_points -= 1
            
            # if ship has no more hit points left, destroy and set flag
            if not hit_ally._hit_points:
                hit_ally.kill()
        
        # check for player kills
        hit_hostiles = groupcollide(sprite_groups['ships']['hostile'],
                                  sprite_groups['lasers']['ally'],
                                      False,
                                      True,
                                      collide_mask)
        
        for hit_hostile in hit_hostiles:
            # update hit ship's hit points attribute
            hit_hostile._hit_points -= 1
            
            # if ship has no more hit points left, destroy and flag
            if not hit_hostile._hit_points:
                hit_hostile.kill()
                
    def _get_level_status(self,
                          sprite_group):
        '''Util function that checks sprite_groups to see if player is dead or all enemies are dead.
        Returns one of three level statuses: fail, success or ongoing.'''
        
        # are any allies (including player) left?
        are_allies_dead = not len(sprite_group['ships']['ally'].sprites())
        
        # are any hostiles (including player) left?
        are_hostiles_dead = not len(sprite_group['ships']['hostile'].sprites())
        
        if are_allies_dead:
            return 'fail'
        elif are_hostiles_dead:
            return 'pass'
        else:
            return 'ongoing'
        
    def _sync_player_(self,player_sprite):
        '''Takes a ShipSprite class object and syncs its _d_speed and _d_angle
        attributes with the keyboard state. This is to avoid weird movement 
        when arrow keys are pressed while player is spawned.'''
        
        pressed_keys = pg.key.get_pressed()
        
        # sync player angle attributes
        if pressed_keys[pg.K_LEFT]:
            player_sprite._d_angle += player_sprite._d_angle_degrees_per_frame
        if pressed_keys[pg.K_RIGHT]:
            player_sprite._d_angle -= player_sprite._d_angle_degrees_per_frame
            
        # sync player speed attributes
        if pressed_keys[pg.K_UP]:
            player_sprite._d_speed += player_sprite._d_speed_pixel_per_frame
        if pressed_keys[pg.K_DOWN]:
            player_sprite._d_speed -= player_sprite._d_speed_pixel_per_frame
            
    def _get_id_image(self,
                      ship_id,
                      size=(50,50)):
        '''Takes the ship_id and makes and returns a pygame surface with that 
        ID in the bottom right corner.'''
        
        largeText = pg.font.Font('freesansbold.ttf',12)
        textSurface = largeText.render(ship_id, True, (254,254,254))
        
        return [textSurface]
    
    def _get_ship_id(self,
                     side,
                     id_no=None):
        '''Util function that formats a ship's side (i.e. 'ally', 'hostile' or
        'player') and its id number into a label displayed on the tracking frame.'''
        
        if side in ['ally','hostile']:
            ship_id = side[0].upper() + side[1:] + str(id_no)
        elif side == 'player':
            ship_id = side[0].upper() + side[1:]
        
        return ship_id
    
    def _get_other_side(self,
                        side):
        '''Util function that gets the opposite side of the side specified as 
        input argument.'''
        
        if side in ['player','ally']:
            other_side = 'hostile'
        elif side == 'hostile':
            other_side = 'ally'
            
        return other_side
    
    def _get_ship_init_args(self,
                            side,
                            ship_no,
                            level_meta_data,
                            level_sprite_groups):
        '''Util function that collects the positional and keyword arguments for the appropriate
        Ship sprite class initializer.'''
        
        data = level_meta_data
        groups = level_sprite_groups
        
        # get hostile side
        other_side = self._get_other_side(side)
        
        # line up positional arguments for sprite initializer
        ship_init_args = [self.fps,
                          self.screen,
                          data['ship_images'][side],
                          data['gun_offsets'][side],
                          data['fire_modes'][side],
                          groups['lasers'][side],
                          data['laser_sounds'][side],
                          data['laser_images'][side],
                          1.2,  # laser range in seconds
                          150, # laser speed in pixel per second
                          1.5, # laser rate of fire in seconds
                          data['muzzle_flash_images'][side],
                          data['muzzle_flash_spi'][side],
                          data['explosion_sounds'],
                          data['explosion_images'],
                          data['explosion_spi'],#self.explosion_spi, # seconds per image for explosions animation at death
                          data['engine_offsets'][side],#self.allied_engine_offsets,
                          data['engine_images'],#self.engine_images,
                          data['engine_spi'],#self.engine_spi,
                          groups['non_colliders']['any'],#self.animations,
                          data['piloting_cone_sine'], # only neede for AIShipSPrite
                          data['gunning_cone_sine'], # only neede for AIShipSPrite
                          (groups['ships'][side],groups['ships']['any'])]#(self.allied_ships,self.all_ships),]
                          
        # get initial values for ship sprite initializers from level meta data
        if side == 'player':
            # adjsut args for player
            ship_init_args = ship_init_args[:20] + ship_init_args[22:]
            
            # get kwargs for player
            ship_init_kwargs = level_meta_data['ship_init_kwargs'][side]
            
        elif side in ['ally','hostile']:
            # get kwargs meta data for squadron
            ships_init_kwargs = level_meta_data['ship_init_kwargs'][side]
            
            # get kwargs for AI single sAI ship
            ship_init_kwargs = dict([(init_type,init_value[ship_no]) for (init_type,init_value) in ships_init_kwargs.items()])
        
            # manually add hostile ship group to single AI hsip's kwargs        
            ship_init_kwargs['hostile_ships_group'] = groups['ships'][other_side] # only neede for AIShipSPrite

        # manually add the sip_id to kwargs
        ship_id = self._get_ship_id(side,
                                    ship_no)
        ship_init_kwargs['ship_id'] = ship_id
            
        return ship_init_args, ship_init_kwargs
            
    def _get_tracking_image(self,
                            side,
                            ship_id):
        
        '''Util function that creates a surface with colored frame indicating
        ship allegiance, as well as the ship id.'''
        
        # create ground surface
        #tracking_canvas = pg.Surface((70,70))
        #tracking_canvas.fill((255,255,255))
        
        # load appropriate frame image and blit to tracking canvas
        ship_frame_image = pg.image.load("./graphics/misc/" + side + "_frame.bmp")
        #tracking_canvas.blit(ship_frame_image,(10,10)) # frme is 50x50, so this should center it
        
        # create text surface
        #largeText = pg.font.Font('freesansbold.ttf',12)
        #text_surface = largeText.render(ship_id, True, (250,250,250))
        
        # superimpose ship id label on ship frame surface
        #tracking_canvas.blit(text_surface,(0,50))
        
        # set color key to ensure only white parts are transparent
        #tracking_canvas.set_colorkey((255,255,255))
        
        return ship_frame_image
        
    def _attach_visual_frame(self,
                             ship,
                             frame_image,
                             sprite_groups):
        
        '''Util function to attach a ship frame with ship id label to a given
        ShipSprite object as a tracking animation.'''
        
        TrackingAnimation(self.fps,
                      self.screen,
                      [frame_image],
                      10000,
                      ship,
                      np.array([0,0]).astype('float'),
                     [sprite_groups['non_colliders']['any']],
                     looping = True,
                     dynamic_angle = False)
        
    def _create_ship_id_card(self,
                             side,
                             new_ship,
                             ship_no,
                             level_meta_data,
                             level_sprite_groups):
        '''Util function that adds a ship's stats id card to the appropriate group.'''
        
        # get pilot images
        pilot_images = level_meta_data['pilot_images'][side]
        
        # get sprite group(s)
        ship_bio_group = level_sprite_groups['cockpit']['any']
        
        # create side-> center_x mapping
        center_x = {'player':1360,
                    'ally':1360,
                    'hostile':100}
        
        # get center coordinates for ship stats id card
        center_pos = (center_x[side],300 + ship_no * 130)
        
        # create the ship stats id card
        ShipBio(pilot_images,
                 new_ship,
                 [ship_bio_group],
                 center = center_pos)
        
        
            
    def spawn_ship(self,
                   side,
                   ship_no,
                   level_meta_data,
                   level_sprite_groups):
        
        '''Initializes an AIShipSprite or a ShipSprite class object with the 
        specified initial values.'''
        
        # select initializer of appropriate sprite class
        if side in ['ally','hostile']:
            Ship = AIShipSprite
        elif side == 'player':
            Ship = ShipSprite
        
        # get ship id
        ship_id = self._get_ship_id(side,ship_no) # not used for now
        
        # collect arguments for the ship sprite initializer - from meta data
        ship_args, ship_kwargs = self._get_ship_init_args(side,
                                                          ship_no,
                                                          level_meta_data,
                                                          level_sprite_groups)

        # create new ship sprite            
        new_ship = Ship(*ship_args,
                        **ship_kwargs)
        
        # create tracking frame image
        tracking_image = self._get_tracking_image(side,
                                                  ship_id)
        
        self._attach_visual_frame(new_ship,
                                  tracking_image,
                                  level_sprite_groups)
        
        # create ship stats "id card" in cockpit frame
        self._create_ship_id_card(side,
                                  new_ship,
                                  ship_no,
                                  level_meta_data,
                                  level_sprite_groups)
        
        
        
        # if player sprite was created, return the created sprite object
        if side == 'player':
            return new_ship
        
    def spawn_squadron(self,
                       side,
                       level_meta_data,
                       level_sprite_groups):
        '''Util function that spawns a group of AIShipSprites for specified
        side, with specified initial values.'''
        
        # iterate over all ships in squadron and spawn
        for ship_index in range(len(level_meta_data['ship_init_kwargs'][side]['center'])):
            
            # spawn inidivual ship
            self.spawn_ship(side,
                            ship_index,
                            level_meta_data,
                            level_sprite_groups)
            
    def spawn_level_ending_messages(self,
                                    level_sprite_groups):
        '''Util function that renders the level endings messages and adds them
        to the level's message sprite groups.'''
        
        # set up specs for pass and fail messages
        level_ending_specs = {'pass':{'message':'MISSION COMPLETE',
                                      'sub_message':None,
                                      'wait_seconds':1.5},
            'fail':{'message':'MISSION FAIL',
                    'sub_message':'Press [Q] to quit, [R] to retry',
                    'wait_seconds':0}}
            
        for level_ending in level_ending_specs.keys():
            self.blit_message_and_wait(level_ending_specs[level_ending]['message'],
                                       sub_message=level_ending_specs[level_ending]['sub_message'],
                                       wait_seconds=level_ending_specs[level_ending]['wait_seconds'],
                                       blit_mode=False,
                                       text_groups=[level_sprite_groups['level_endings'][level_ending]])
            
def main():
    # make sure directory is repo head
    os.chdir('..')
    
    
    Game()
    
if __name__=='__main__':
    main()