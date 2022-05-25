import pygame
import time
import controllers
import components
import actions
import colors
import random
import settings
import spatial_hashing
import helpers
from pathlib import Path
import os
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

class Game:
    def __init__(self, screen, collision_grid_width):
        self.screen = screen
        self.collision_grid_width = collision_grid_width

        self.actions = actions
        self.colors = colors
        self.helpers = helpers
        self.controllers = controllers
        self.components = components
        #TODO Fix this action controller system at some point
        self.action_handler = actions.ActionHandler(self, components.controller_sys)
        self.camera = Camera(self)
        GM = spatial_hashing.GridManager

        self.images = {}
        self.animation_images = {}
        self.entities = {}
        self.entity_props = {}
        self.living_entities = 0
        self.last_id = 0

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.collision_maps = {}
        for category in settings.COLLISION_CATEGORIES:
            self.collision_maps[category] = GM(self.collision_grid_width)
    
    def get_unique_id(self):
        """Returns an int that's unique each time it's called"""

        self.last_id += 1
        return self.last_id - 1
    
    def is_alive(self, entity_id):
        """Return whether the given entity exists in entities still"""

        return entity_id in self.entities
    
    def create_entity(self, entity_id):
        """Adds a new id to the list of entities without any components yet"""

        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(components.system_index)
        # Each entity is just an id number connected to a list of component indexes
        self.entities[entity_id] = component_indexes
        self.living_entities += 1
        self.entity_props[entity_id] = {}

    def add_component(self, entity_id, component_name, *args, **kwargs):
        """Changes the value for the given component in that entity's list of
        component indexes from -1 to whatever the next open spot is"""

        index = components.systems[component_name].add_component(self, entity_id, *args, **kwargs)
        self.entities[entity_id][components.component_index[component_name]] = index
        return entity_id
    
    def add_property(self, entity_id, property, value):
        """Adds a new property to an entity such as health or damage."""

        self.set_property(entity_id, property, value)
    
    def destroy_entity(self, entity_id):
        """Deactivates each of the components of an entity, and remove the id from
        the list of entities."""

        try:
            for i, index in enumerate(self.entities[entity_id]):
                if index != -1:
                    components.system_index[i].remove_component(index)
            self.entities.pop(entity_id)
            self.entity_props.pop(entity_id)
            self.living_entities -= 1
        except:
            pass

    def get_component(self, entity_id, component_name):
        """Gives a reference of a component of an entity."""

        try:
            component = self.components.systems[component_name].components[self.entities[entity_id][components.component_index[component_name]]]
            return component
        except KeyError:
            raise KeyError(f"Component `{component_name}` or entity `{entity_id}` does not exist.")
    
    def get_property(self, entity_id, property):
        """Gives a reference of a property of an entity."""

        return self.entity_props[entity_id][property]
    
    def set_property(self, entity_id, property, value):
        """Changes the value of an entity's property."""

        self.entity_props[entity_id][property] = value
    
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


def show_fps(fps_font):
    """This function just displays the current fps in the topleft corner."""
    
    clock.tick()
    font = fps_font.render(f"Entities: {game.living_entities}, FPS: {round(clock.get_fps())}", False, colors.blue)
    fps_rect = font.get_rect()
    fps_rect.topleft = 0, 0
    screen.blit(font, fps_rect)


if __name__ == "__main__":
    clock = pygame.time.Clock()
    FPS_FONT = pygame.font.SysFont("couriernew", 15)
    screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.RESIZABLE)

    game = Game(screen, settings.COLLISION_GRID_WIDTH)
    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    game.update_images(load_images(), load_animation_images())
    id = game.get_unique_id()
    game.add_action(actions.SpawnPlayer(id, Vector2(0, 0), 0, 1, settings.PLAYER_MAX_SPEED, settings.PLAYER_ACCEL, settings.PLAYER_DECEL, settings.PLAYER_FRICTION))
    game.add_action(actions.FocusCamera(id, True))
    for i in range(1):
        enemy_id = game.get_unique_id()
        game.add_action(actions.SpawnEnemy(enemy_id, Vector2(random.randint(-500, 500), random.randint(-500, 500)), 0, 1, settings.PLAYER_MAX_SPEED, settings.PLAYER_ACCEL, settings.PLAYER_DECEL, settings.PLAYER_FRICTION))
        game.add_action(actions.StartFiringBarrels(enemy_id))

    helpers.spawn_shapes(game, 60, [Vector2(-1000, -1000), Vector2(1000, 1000)])

    game.action_handler.handle_actions()

    while True:
        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time
        components.life_timer_sys.update()

        game.action_handler.get_player_input()
        components.controller_sys.update()
        components.barrel_manager_sys.update()


        while game.accumulator >= game.dt:
            try:
                game.get_component(enemy_id, "transform").rotation += 100 * game.dt
            except:
                pass
            components.physics_sys.update(game.dt)
            game.camera.update()
            components.collider_sys.update()
            game.action_handler.handle_actions()
            game.accumulator -= game.dt
        
        screen.fill(colors.white)
        game.camera.draw_grid()
        components.graphics_sys.update()
        components.health_bar_sys.update()
        pygame.draw.rect(screen, colors.black, (1, 1, screen.get_width(), screen.get_height()), 3)
        show_fps(FPS_FONT)
        pygame.display.update()