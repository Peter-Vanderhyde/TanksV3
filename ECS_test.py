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
from pathlib import Path
from pygame.locals import *
from pygame.math import Vector2
pygame.init()

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
    animation_images = {}
    for path in Path(settings.ANIMATION_PATH).rglob("*.png"):
        path_string = '/'.join(path.parts).removeprefix(settings.ANIMATION_PATH).removesuffix(".png")
        # This makes 3 strings separated by '/'. The first is the animation set's name, then the specific
        # animation, then the image name
        image = pygame.image.load(path).convert_alpha()
        image.set_colorkey((255, 255, 255))
        animation_images.update({path_string:image})
    
    return animation_images

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

        self.ui_manager = ui.UI_Manager(self)
        #TODO Fix this action controller system at some point
        self.action_handler = actions.ActionHandler(self)
        self.camera = Camera(self)
        self.grid_manager = spatial_hashing.GridManager

        self.images = {}
        self.animation_images = {}
        self.dt = 0.01
        self.accumulator = 0.0

        self.fps_text = ui.Text("couriernew", 15, colors.blue)

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
    
    def create_entity(self, entity_id):
        """Adds a new id to the list of entities without any components yet"""

        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(self.get_system_index())
        # Each entity is just an id number connected to a list of component indexes
        self.get_entities()[entity_id] = component_indexes
        self.set_living_entities(self.get_living_entities() + 1)
        self.get_entity_props()[entity_id] = {}

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
    
    def update_images(self, new_images_dict, new_anim_images_dict):
        """Takes a dictionaries of images and adds them to the dictionaries of images
        and animation_images."""

        self.images.update(new_images_dict)
        self.animation_images.update(new_anim_images_dict)

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
    game.update_images(load_images(), load_animation_images())
    return game

if __name__ == "__main__":
    screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.RESIZABLE)

    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    scene_manager = state_machine.SceneManager(screen, "main menu")
    scene_manager.start()