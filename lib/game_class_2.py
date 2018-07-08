# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:09:47 2018

@author: Atreju Maischberger
"""

# demo gam states here
import sys
import os
import yaml

import pygame as pg
import numpy as np

from pygame.sprite import Group, collide_mask, groupcollide
from sprite_classes import ShipSprite, AIShipSprite
from animation_classes import TrackingAnimation

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
        
        self.background_image = pg.image.load('./graphics/misc/star_wars_background_24bit.bmp')
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
            
        # set player, ally and hostile ship and laser types
        player_ship, player_laser = 'xwing' ,'red'
        ally_ship, ally_laser = 'awing', 'red'
        hostile_ship, hostile_laser = 'tiefighter', 'green'
        
    def _collect_meta_data_for_level(self,
                                     level_specs):
        '''Util function that collects all the sprite related meta data for player,
        allies and hostiles for current level.
        Input argument is
        - level_specs: dictionary. Contains the keys
            - 'level_number': integer
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
                          'level_number':level_specs['level_number']}
        
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
        
        level_sprite_groups = {'ships':ship_groups,
                              'lasers':laser_beams_groups,
                              'non_colliders':non_collidables_group}
        
        return level_sprite_groups
    
    def _spawn_ships_for_level(self,
                               level_meta_data,
                               level_sprite_groups):
        '''Util function that spawns all the ships for current level. Returns the
        intitalized player ShipSprite object.'''
        # create player sprite and add to relevant groups / provide with relevant groups
        player = self.spawn_ship('player',
                                 0,
                                 level_meta_data,
                                 level_sprite_groups)
        
        # create allies for this level and blit to screen
        self.spawn_squadron('ally',
                            level_meta_data,
                            level_sprite_groups)
        
        # create hostiles for this level and blit to screen
        self.spawn_squadron('hostile',
                            level_meta_data,
                            level_sprite_groups)
        
        return player
        
        
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
        
        # spawn ships for this level
        player = self._spawn_ships_for_level(level_meta_data,
                                             level_sprite_groups)
        
        # initialize pause state variable
        paused = False
        
        # initiazlie sound toggle variable
        sound = False
        
        # start main game loop
        while True:
            # check for exit events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    
                    # quit pygame
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    
                    # toggle pause state if needed
                    if event.key == pg.K_ESCAPE:
                        paused = not paused
                        
                    # toggle sound if needed
                    if event.key == pg.K_s:
                        sound = not sound
                        
                        # update sprites if needed
                        for ship in self.all_ships.sprites():
                            ship._sound = sound
                    
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
                
            if not paused:
            
                # update game state
                self.update_game_state(level_sprite_groups)
                
                # draw update game state to screen
                self.draw_game_state(level_sprite_groups)
                
                # check and handle collisions
                self.handle_collisions(level_sprite_groups)
                        
            # control pace
            self.clock.tick(self.fps)
            
    def update_game_state(self,
                          sprite_groups):
        '''Updates the game state by updating all the game's sprite groups.'''
        
        sprite_groups['ships']['any'].update()
        sprite_groups['lasers']['ally'].update()
        sprite_groups['lasers']['hostile'].update()
        sprite_groups['non_colliders']['any'].update()
        
    def draw_game_state(self,
                        sprite_groups):
        '''Draws updated game state by wiping the game's main surface,
        drawing all the game's sprite groups and then flipping the game's main
        surface to display the drawings.'''
        
        # draw new game state    
        self.screen.blit(self.background_image,(0,0)) # paint over old game state
        
        sprite_groups['ships']['any'].draw(self.screen)
        sprite_groups['lasers']['ally'].draw(self.screen)
        sprite_groups['lasers']['hostile'].draw(self.screen)
        sprite_groups['non_colliders']['any'].draw(self.screen)
                   
        # flip canvas
        pg.display.flip()
        
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
            ship_init_kwargs = level_meta_data['ship_init_kwargs'][side]
        elif side in ['ally','hostile']:
            ship_init_kwargs = level_meta_data['ship_init_kwargs'][side][ship_no]
            
        ship_init_kwargs['hostile_ships_group'] = groups['ships'][other_side] # only neede for AIShipSPrite
        
        # adjust args and kwargs if a ShipSprite (and no AIShipSprite) will be initialized
        if side == 'player':
            # adjsut args
            ship_init_args = ship_init_args[:20] + ship_init_args[22:]
            
            # adjust kwargs
            del ship_init_kwargs['hostile_ships_group']
            
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
                             frame_image):
        
        '''Util function to attach a ship frame with ship id label to a given
        ShipSprite object as a tracking animation.'''
        
        TrackingAnimation(self.fps,
                      self.screen,
                      [frame_image],
                      10000,
                      ship,
                      np.array([0,0]).astype('float'),
                     [self.sprite_groups['non_colliders']['any']],
                     looping = True,
                     dynamic_angle = False)
            
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
        
        # collect arguments for the ship sprite initializer
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
                                  tracking_image)
        
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
        for ship_index in range(level_meta_data['ship_init_kwargs'][side]['centers']):
            
            # spawn inidivual ship
            self.spawn_ship(side,
                            ship_index,
                            level_meta_data,
                            level_sprite_groups)
        
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
            
def main():
    # make sure directory is repo head
    os.chdir('..')
    
    
    Game()
    
if __name__=='__main__':
    main()