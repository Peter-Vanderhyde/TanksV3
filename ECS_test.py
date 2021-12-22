import pygame
import sys
import random
import time
import components
import actions
import colors
import settings
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


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.components = components
        self.actions = actions
        self.images = {}

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.entities = {}
        self.living_entities = 0
        self.last_id = 0

        self.action_handler = actions.ActionHandler(self, components.controller_sys)
        self.camera = Camera(self)
    
    def get_unique_id(self):
        self.last_id += 1
        return self.last_id
    
    def create_entity(self, entity_id):
        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(components.system_index)
        # Each entity is just this list of component indexes associated with an id key
        self.entities[entity_id] = component_indexes

    def add_component(self, entity_id, component_name, *args, **kwargs):
        index = components.systems[component_name].add_component(self, entity_id, *args, **kwargs)
        self.entities[entity_id][components.component_index[component_name]] = index
        return entity_id
    
    def destroy_entity(self, entity_id):
        try:
            for i, index in enumerate(self.entities[entity_id]):
                if index != -1:
                    components.system_index[i].remove_component(index)
            self.entities.pop(entity_id)
        except:
            pass

    def get_component(self, entity_id, component_name):
        try:
            component = components.systems[component_name].components[self.entities[entity_id][components.component_index[component_name]]]
            return component
        except KeyError:
            raise KeyError("Tried to get component that does not exist.")
    
    def add_action(self, action):
        self.action_handler.add_action(action)
    
    def update_images(self, new_images_dict):
        self.images.update(new_images_dict)


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
            if jump:
                self.set_position(self.target)
        except KeyError:
            raise AttributeError("Camera target does not exist or does not have a transform component.")
    
    def set_position(self, position):
        self.corner = Vector2(position.x - self.width // 2, position.y - self.height // 2)
    
    def update(self):
        if self.target is not None:
            center = Vector2(self.corner.x + self.width // 2, self.corner.y + self.height // 2)
            self.velocity = self.velocity.lerp((Vector2(self.target.x, self.target.y) - center) * 4, 1)

            self.corner += self.velocity * self.game.dt
    
    def draw_grid(self):
        # Draw grid lines
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


if __name__ == "__main__":
    screen = pygame.display.set_mode(settings.SCREEN_SIZE)

    game = Game(screen)
    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    game.update_images(load_images())
    id = game.get_unique_id()
    game.add_action(actions.SpawnPlayer(id, Vector2(300, 300), 0, 1, settings.PLAYER_MAX_SPEED, settings.PLAYER_ACCEL, settings.PLAYER_FRICTION))
    game.add_action(actions.FocusCamera(id, True))

    while 1:
        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time

        game.action_handler.handle_actions()

        while game.accumulator >= game.dt:
            components.physics_sys.update(game.dt)
            game.camera.update()
            game.accumulator -= game.dt
        
        game.action_handler.get_player_input()
        components.controller_sys.update()
        
        screen.fill(colors.white)
        game.camera.draw_grid()
        components.graphics_sys.update(screen)
        pygame.display.update()