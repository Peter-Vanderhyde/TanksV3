from pathlib import Path
import pygame
import camera
import controllers
import components
import actions
import colors
import settings
import spatial_hashing
import helpers
import animations
import ui
import state_machine
import math
import time
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.mixer.init()

#TODO
# Find some way so that there is a base thing for movement, so it just calls update on all the move things
#   so they can update accordingly. Maybe they all need the camera or something.
# I have a suspicion that the reason the barrel is stuck small sometimes while shooting is because
#   it is getting multiple requests to play the same shooting animation within a brief period
#   (ie I click the mouse multiple times). Should I disable the ability to run the same animation at the same
#   time it's already playing? Probably. It might actually already be checking for that when it's playing.
#   Anyway check if the barrel bug has something to do with that.
# Give tanks a "lock weapons" property so they can't shoot until allowed.
# ^ also add to the on finish property to allow it to change any property of itself and set it to any value.
#   Then you can make it so after the entire spawning animation is done it "unlocks" the weapons.
# Make health spin slower
# Only make health collectible of health under 100%
# Add ability to slow time
# Only enable shooting once spawn animation is finished
# Make death screen
# Make the collectible particles add xp not health
# Add slight magnetics?
# Make a random chance to drop and random amount of them
# Make sounds get quieter
# Make shapes destructible
# Instead of wall, make it so if you cross the border, a line connects to you and, the longer
#   you stay out of bounds, the more the line goes from green to red and then pulls you back (maybe damages too)
# Make small enemies that slowly go for player
# Explosions consist of randomly orange particles going from color to gray and shrinking
# Also just smoke particles (But not too many)
# Make the experience indicator be on the tank's body
# Add a UI element for creating outlines and boxes that can have curved edges and such.
# Make one such element for the main menu. Maybe use one in-game to display stats on the side.
# (For crazy idea, instead of changing the background of the button rect so the background bleeds around the curved
#  edge, try making the background transparent and drawing a completely different rect behind it with the same rounding)
# Add engines
# Add slight variation to shooting

def load_image(name, alpha=True, colorkey=()):
    if alpha:
        image = pygame.image.load(settings.IMAGE_PATH + name + ".png").convert_alpha()
        if colorkey != ():
            image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(settings.IMAGE_PATH + name + ".png").convert()
    return image

def load_images():
    """settings.IMAGES is a tuple of tuples, each of which contain
    (image name, alpha bool, colorkey color)"""
    images_dict = {}
    for asset in settings.IMAGES:
        image = load_image(*asset)
        images_dict.update({asset[0]:image})
    
    return images_dict

def load_animation_images():
    """Searches through the animations folder for any png images, loads the image, then saves it
    in the game's images dictionary as {image_path:image_object}. It then returns the full dictionary."""

    # This is first called to correctly format any animations using the "create frames" option.
    # [More Info](animation_syntax.pdf#Create Frames)
    animations.format_animations()
    # A container to store all animations as {image_path:image_obj}
    animation_images = {}
    for path in Path(settings.ANIMATION_PATH).rglob("*.png"):
        path_string = '/'.join(path.parts).removeprefix(settings.ANIMATION_PATH).removesuffix(".png")
        # This makes 3 strings separated by '/'. The first is the animation set's name, then the specific
        # animation, then the image name
        image = pygame.image.load(path).convert_alpha()
        # Automatically make white the alpha colorkey of the image unless otherwise specified in the settings
        if path.parts[-3] + "/" + path.parts[-4] not in settings.ANIMATION_COLORKEY_EXCLUSION:
            image.set_colorkey((255, 255, 255))
        
        animation_images.update({path_string:image})
    
    return animation_images

def load_sounds():
    # Save the sounds as {sound_string:sound}
    sounds = {}
    for sound in settings.SOUNDS:
        sound_name, sound_file = sound
        sounds[sound_name] = pygame.mixer.Sound(settings.SOUND_PATH + "/" + sound_file)
    
    return sounds

class Container:
    """
    This container is used as a way to easily interact with the state container which is holding all of the game data.
    It makes an easy way to save and restore states.
    """
    def __init__(self, state_container):
        # The state container holds the game data. The data can be saved and loaded at will.
        self.state_container = state_container
    
    def get_systems(self):
        return self.state_container.systems
    
    def get_component_index(self):
        return self.state_container.component_index
    
    def get_system_index(self):
        return self.state_container.system_index
    
    def get_entities(self):
        return self.state_container.entities
    
    def get_entity_props(self):
        return self.state_container.entity_props
    
    def get_living_entities(self):
        return self.state_container.living_entities
    
    def get_last_id(self):
        return self.state_container.last_id
    
    def get_collision_maps(self):
        return self.state_container.collision_maps
    
    def get_player(self):
        return self.state_container.player
    
    def set_living_entities(self, living_entities):
        self.state_container.living_entities = living_entities
    
    def set_last_id(self, last_id):
        self.state_container.last_id = last_id
    
    def set_player(self, player_id):
        self.state_container.player = player_id

class Game(Container):
    """
    This holds all of the information about the current game/state instance. The scene manager can
    choose to overwrite the data with data in the state container instead.
    """
    def __init__(self, screen, collision_grid_width, scene_manager):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.collision_grid_width = collision_grid_width
        self.scene_manager = scene_manager

        self.actions = actions
        self.colors = colors
        self.settings = settings
        self.helpers = helpers
        self.controllers = controllers
        self.components = components
        # The dictionary holding the json animation data
        self.animations = animations.animations
        # The dictionary holding instances of each state
        self.states = state_machine.states
        self.ui = ui

        #TODO Fix this action controller system at some point
        self.action_handler = actions.ActionHandler(self)
        self.camera = camera.Camera(self)
        self.grid_manager = spatial_hashing.GridManager

        self.images = {}
        self.animation_images = {}
        self.sounds = {}
        self.dt = 0.01
        self.accumulator = 0.0
        self.game_speed = 1.0
        self.sounds_to_play = []
        # Allows the maximum number of sounds to play simultaneously
        pygame.mixer.set_num_channels(settings.MAX_SOUND_CHANNELS)

        # This now holds all of the things that change from state to state
        # so when saving a state, this is what you save.
        state_container = state_machine.StateContainer(self)
        super().__init__(state_container)
    
    def get_unique_id(self):
        """
        Returns an int that's unique each time it's called.
        """

        last_id = self.get_last_id()
        self.set_last_id(last_id + 1)
        return last_id
    
    def is_alive(self, entity_id):
        """
        Return whether the given entity exists in entities still.
        """

        return entity_id in self.get_entities()
    
    def create_entity(self, entity_id, trigger_on_death=None, args=None):
        """
        Adds a new id to the list of entities without any components yet.
        """

        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(self.get_system_index())
        # Each entity is just an id number connected to a list of component indexes
        self.get_entities()[entity_id] = component_indexes
        # Increase the number of living entities by 1
        self.set_living_entities(self.get_living_entities() + 1)
        # Initialize the properties of the entity as an empty dictionary. This will hold whatever
        # data is necessary for the entity such as health, damage, etc.
        self.get_entity_props()[entity_id] = {}

        # Pass in a function to be executed upon the entity's death
        if trigger_on_death:
            self.get_entity_props()[entity_id]["on death"] = trigger_on_death
        if args:
            self.get_entity_props()[entity_id]["on death args"] = args

    def add_component(self, entity_id, component_name, *args, **kwargs):
        """
        Changes the value of the given component in that entity's list of
        component indexes from -1 to the index of that component in its component list.
        """

        # Takes the next available unused component instance and initialize it
        index = self.get_systems()[component_name].add_component(self, entity_id, *args, **kwargs)
        # Save its index to be able to reference it in future as this entity's component
        self.get_entities()[entity_id][self.get_component_index()[component_name]] = index
        return entity_id
    
    def add_property(self, entity_id, property, value):
        """
        Adds a new property to an entity such as health or damage.
        """

        self.set_property(entity_id, property, value)
    
    def destroy_entity(self, entity_id):
        """
        Deactivates each of the components of an entity, and remove the id from
        the list of living entities.
        """

        try:
            for i, index in enumerate(self.get_entities()[entity_id]):
                if index != -1:
                    # Deactivate that component (ie mark it as not in use)
                    self.get_system_index()[i].remove_component(index)
            # Remove entity id from the list of living entities to remove any reference to it.
            self.get_entities().pop(entity_id)
            if "on death" in self.get_entity_props()[entity_id]:
                # Call any functions that were set to be called when this entity died
                if "on death args" in self.get_entity_props()[entity_id]:
                    # Uses these two special keys
                    self.get_entity_props()[entity_id]["on death"](self.get_entity_props()[entity_id]["on death args"])
                else:
                    self.get_entity_props()[entity_id]["on death"]()
            
            # Remove id from the list of ids
            self.get_entity_props().pop(entity_id)
            # One less living entity
            self.set_living_entities(self.get_living_entities() - 1)
        except:
            # Usually fails if it has already been removed
            pass
    
    def has_component(self, entity_id, component_name):
        """
        Checks if an entity has a component without raising an error.
        """

        try:
            _ = self.get_component(entity_id, component_name)
            return True
        except KeyError:
            return False

    def get_component(self, entity_id, component_name):
        """
        Gives a reference of a component of an entity.
        """

        try:
            # Get the list of all of the instances of this component type
            list_of_components = self.get_systems()[component_name].components
            # Get what index position is used for this component type in the entity's component list
            index_position_of_component_type = self.get_component_index()[component_name]
            # Check what index is stored at that position in the component list
            index_of_component = self.get_entities()[entity_id][index_position_of_component_type]
            # Use that index value to get a reference to the correct component in the list of components
            component = list_of_components[index_of_component]
            return component
        except KeyError:
            raise KeyError(f"Component `{component_name}` or entity `{entity_id}` does not exist.")
    
    def get_property(self, entity_id, property):
        """
        Gives a reference of a property of an entity.
        """

        return self.get_entity_props()[entity_id][property]
    
    def set_property(self, entity_id, property, value):
        """
        Changes the value of an entity's property.
        """

        self.get_entity_props()[entity_id][property] = value
    
    def add_action(self, action):
        """
        Append an action onto the handler's queue to be executed next cycle.
        """

        # Actions are anything that the game will need to do such as creating some entity,
        # destroying an entity, firing a weapon, etc.
        self.action_handler.add_action(action)
    
    def update_images_and_sounds(self, new_images_dict, new_anim_images_dict, new_sounds_dict):
        """
        Combines the given dictionaries of images and sounds with the current dictionaries.
        """

        self.images.update(new_images_dict)
        self.animation_images.update(new_anim_images_dict)
        self.sounds.update(new_sounds_dict)
    
    def resync_components(self):
        """
        Fix any discrepencies that may occur from switching between different game states.
        """
        
        # time_since_save = time.time() - self.state_container.time_of_save
        # No longer needed since components don't calculate based off time.time anymore
        
        for controller in self.get_systems()["controller"].components:
            if controller.id is not None and controller.controller_name == "player":
                # Stops shooting when a menu has been closed so that they are not shooting without
                # clicking.
                self.add_action(self.actions.StopFiringBarrels(controller.id))
    
    def play_sound(self, sound, position):
        """
        Adds sounds to the list of sounds to be played upon the next game loop update.
        """
        
        self.sounds_to_play.append((sound, position, time.time()))

    def play_sounds(self):
        """
        Play all possible sounds from the list of sounds that need to be played.
        """
        
        current_time = time.time()
        # Copy the list of sounds so that the popping that occurs in the for loop does not
        # affect the for loop
        for sound_info in self.sounds_to_play[:]:
            free_channel = pygame.mixer.find_channel()
            if free_channel: # Not all channels are currently busy playing a sound
                # Try to make the sound quieter based on how close it is to the player
                sound, sound_position, play_requested = sound_info
                sound_position = Vector2(sound_position)
                camera_pos = self.camera.corner + (self.camera.width / 2, self.camera.height / 2)
                distance_from_source = abs((camera_pos - sound_position).length())
                curr_volume = sound.get_volume() # sound objects keep track of the volume they are previously set to
                new_volume = curr_volume
                new_volume -= settings.SOUND_FALLOFF_RATE * math.sqrt(distance_from_source)
                if new_volume <= 0:
                    # The sound was too quiet to hear anyway so remove from queue
                    self.sounds_to_play.remove(sound_info)
                else:
                    sound.set_volume(new_volume)
                    free_channel.play(sound)
                    self.sounds_to_play.remove(sound_info)
            else:
                _, _, play_requested = sound_info
                if current_time - play_requested >= 0.25:
                    self.sounds_to_play.remove(sound_info)


def create_game_instance(scene_manager):
    """
    Creates a fresh game whenever the program is first run.
    """
    
    game = Game(scene_manager.screen, settings.COLLISION_GRID_WIDTH, scene_manager)
    # Format the animation json data
    animations.load_animations(settings.ANIMATION_PATH)
    game.update_images_and_sounds(load_images(), load_animation_images(), load_sounds())
    return game

if __name__ == "__main__":
    screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.RESIZABLE)

    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    # Set the starting scene as the main menu
    scene_manager = state_machine.SceneManager(screen, "main menu")
    scene_manager.start()