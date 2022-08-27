from pathlib import Path
import pygame
import time
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
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
pygame.init()
pygame.mixer.init()

#TODO
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
    d = {}
    for asset in settings.ASSETS:
        image = load_image(*asset)
        d.update({asset[0]:image})
    
    return d

def load_animation_images():
    animations.format_animations()
    animation_images = {}
    for path in Path(settings.ANIMATION_PATH).rglob("*.png"):
        path_string = '/'.join(path.parts).removeprefix(settings.ANIMATION_PATH).removesuffix(".png")
        # This makes 3 strings separated by '/'. The first is the animation set's name, then the specific
        # animation, then the image name
        image = pygame.image.load(path).convert_alpha()
        if path.parts[-3] + "/" + path.parts[-4] not in settings.ANIMATION_COLORKEY_EXCLUSION:
            image.set_colorkey((255, 255, 255))
        
        animation_images.update({path_string:image})
    
    return animation_images

def load_sounds():
    sounds = {}
    for sound in settings.SOUNDS:
        sounds[sound[0]] = pygame.mixer.Sound(settings.SOUND_PATH + "/" + sound[1])
    
    return sounds

class Container:
    def __init__(self, state_container):
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
    
    def set_living_entities(self, living_entities):
        self.state_container.living_entities = living_entities
    
    def set_last_id(self, last_id):
        self.state_container.last_id = last_id

class Game(Container):
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
        self.animations = animations.animations
        self.states = state_machine.states
        self.ui = ui

        #TODO Fix this action controller system at some point
        self.action_handler = actions.ActionHandler(self)
        self.camera = Camera(self)
        self.grid_manager = spatial_hashing.GridManager

        self.images = {}
        self.animation_images = {}
        self.sounds = {}
        self.dt = 0.01
        self.accumulator = 0.0
        self.sounds_to_play = []
        pygame.mixer.set_num_channels(settings.MAX_SOUND_CHANNELS)

        # This now holds all of the things that change from state to state
        # so when saving a state, this is what you save.
        state_container = state_machine.StateContainer(self)
        super().__init__(state_container)
    
    def get_unique_id(self):
        """Returns an int that's unique each time it's called"""

        last_id = self.get_last_id()
        self.set_last_id(last_id + 1)
        return last_id
    
    def is_alive(self, entity_id):
        """Return whether the given entity exists in entities still"""

        return entity_id in self.get_entities()
    
    def create_entity(self, entity_id, trigger_on_death=None, args=None):
        """Adds a new id to the list of entities without any components yet"""

        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(self.get_system_index())
        # Each entity is just an id number connected to a list of component indexes
        self.get_entities()[entity_id] = component_indexes
        self.set_living_entities(self.get_living_entities() + 1)
        self.get_entity_props()[entity_id] = {}

        # Pass in a function to be executed upon the entity's death
        if trigger_on_death:
            self.get_entity_props()[entity_id]["on death"] = trigger_on_death
        if args:
            self.get_entity_props()[entity_id]["on death args"] = args

    def add_component(self, entity_id, component_name, *args, **kwargs):
        """Changes the value for the given component in that entity's list of
        component indexes from -1 to whatever the next open spot is"""

        index = self.get_systems()[component_name].add_component(self, entity_id, *args, **kwargs)
        self.get_entities()[entity_id][self.get_component_index()[component_name]] = index
        return entity_id
    
    def add_property(self, entity_id, property, value):
        """Adds a new property to an entity such as health or damage."""

        self.set_property(entity_id, property, value)
    
    def destroy_entity(self, entity_id):
        """Deactivates each of the components of an entity, and remove the id from
        the list of entities."""

        try:
            for i, index in enumerate(self.get_entities()[entity_id]):
                if index != -1:
                    self.get_system_index()[i].remove_component(index)
            self.get_entities().pop(entity_id)
            if "on death" in self.get_entity_props()[entity_id]:
                if "on death args" in self.get_entity_props()[entity_id]:
                    self.get_entity_props()[entity_id]["on death"](self.get_entity_props()[entity_id]["on death args"])
                else:
                    self.get_entity_props()[entity_id]["on death"]()
            
            self.get_entity_props().pop(entity_id)
            self.set_living_entities(self.get_living_entities() - 1)
        except:
            pass
    
    def has_component(self, entity_id, component_name):
        """Checks if an entity has a component without raising an error."""

        try:
            component = self.get_component(entity_id, component_name)
            return True
        except KeyError:
            return False

    def get_component(self, entity_id, component_name):
        """Gives a reference of a component of an entity."""

        try:
            component = self.get_systems()[component_name].components[self.get_entities()[entity_id][self.get_component_index()[component_name]]]
            return component
        except KeyError:
            raise KeyError(f"Component `{component_name}` or entity `{entity_id}` does not exist.")
    
    def get_property(self, entity_id, property):
        """Gives a reference of a property of an entity."""

        return self.get_entity_props()[entity_id][property]
    
    def set_property(self, entity_id, property, value):
        """Changes the value of an entity's property."""

        self.get_entity_props()[entity_id][property] = value
    
    def add_action(self, action):
        """Append an action onto the handler's queue to be executed next cycle."""

        self.action_handler.add_action(action)
    
    def update_images_and_sounds(self, new_images_dict, new_anim_images_dict, new_sounds_dict):
        """Takes a dictionaries of images and adds them to the dictionaries of images
        and animation_images."""

        self.images.update(new_images_dict)
        self.animation_images.update(new_anim_images_dict)
        self.sounds.update(new_sounds_dict)
    
    def resync_components(self):
        # time_since_save = time.time() - self.state_container.time_of_save
        # No longer needed since components don't calculate based off time.time anymore
        
        for controller in self.get_systems()["controller"].components:
            if controller.id is not None and controller.controller_name == "player":
                self.add_action(self.actions.StopFiringBarrels(controller.id))
    
    def play_sound(self, sound, position):
        self.sounds_to_play.append((sound, position))

    def play_sounds(self):
        for sound_info in self.sounds_to_play:
            if pygame.mixer.find_channel():
                free_channel = pygame.mixer.find_channel()
                sound, sound_position = sound_info
                sound_position = Vector2(sound_position)
                camera_pos = self.camera.corner + (self.camera.width / 2, self.camera.height / 2)
                distance_from_source = abs((camera_pos - sound_position).length())
                curr_volume = sound.get_volume()
                new_volume = curr_volume
                new_volume -= settings.SOUND_FALLOFF_RATE * math.sqrt(distance_from_source)
                new_volume = max(0, new_volume)
                sound.set_volume(new_volume)
                free_channel.play(sound)
                self.sounds_to_play.pop(0)
            else:
                return
                

class Camera:
    def __init__(self, game, target_id=None):
        self.game = game
        self.target_id = target_id
        self.target = None
        self.velocity = Vector2(0, 0)
        self.corner = Vector2(0, 0)
        self.width, self.height = self.game.screen.get_size()
        if self.target_id is not None:
            self.set_target(self.target_id)

    def set_target(self, target_id, jump=False):
        try:
            self.target = self.game.get_component(target_id, "transform")
            self.target_id = target_id
            if jump:
                self.set_position(self.target)
        except KeyError:
            raise AttributeError("Camera target does not exist or does not have a transform component.")
    
    def clear_target(self):
        self.target_id = None
        self.target = None
    
    def set_position(self, position):
        self.corner = Vector2(position.x - self.width // 2, position.y - self.height // 2)
    
    def update(self):
        if self.target is not None:
            center = Vector2(self.corner.x + self.width // 2, self.corner.y + self.height // 2)
            self.velocity = self.velocity.lerp((Vector2(self.target.x, self.target.y) - center) * 4, 1)

            self.corner += self.velocity * self.game.dt
    
    def draw_grid(self):
        """This function draw the background lines of the grid that move as the
        player does."""

        game = self.game
        grid_box_w, grid_box_h = (settings.GRID_SIZE, settings.GRID_SIZE)

        left_buffer = -self.corner.x % grid_box_w
        for x in range(round(self.width // grid_box_w) + 1):
            x_pos = left_buffer + x * grid_box_w
            pygame.draw.line(game.screen, colors.light_gray, (x_pos, 0), (x_pos, self.height))

        top_buffer = -self.corner.y % grid_box_h
        for y in range(round(self.height // grid_box_h) + 1):
            y_pos = top_buffer + y * grid_box_h
            pygame.draw.line(game.screen, colors.light_gray, (0, y_pos), (self.width, y_pos))


def create_game_instance(scene_manager):
    game = Game(scene_manager.screen, settings.COLLISION_GRID_WIDTH, scene_manager)
    animations.load_animations(settings.ANIMATION_PATH)
    game.update_images_and_sounds(load_images(), load_animation_images(), load_sounds())
    return game

if __name__ == "__main__":
    screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.RESIZABLE)

    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    scene_manager = state_machine.SceneManager(screen, "main menu")
    scene_manager.start()