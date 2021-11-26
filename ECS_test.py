import pygame
import sys
import random
import time
from components import *
from colors import *
from settings import *
from actions import *
from pygame.locals import *
from pygame.math import Vector2
pygame.init()


images = {}

def load_image(name, alpha=True, colorkey=()):
    if alpha:
        image = pygame.image.load(IMAGE_PATH + name + ".png").convert_alpha()
        if colorkey != ():
            image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(IMAGE_PATH + name + ".png").convert()
    return image

def load_images():
    d = {}
    for asset in ASSETS:
        image = load_image(*asset)
        d.update({asset[0]:image})
    
    return d


class Game:
    def __init__(self, screen):
        self.screen = screen

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.entities = {}
        self.living_entities = 0
        self.last_id = 0

        self.action_handler = ActionHandler(self, input_handler_sys)
        self.camera = Camera(self)
    
    def create_entity(self, entity_id):
        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(system_index)
        # Each entity is just this list of component indexes associated with an id key
        self.entities[entity_id] = component_indexes
        self.last_id += 1

    def add_component(self, entity_id, component_name, *args, **kwargs):
        index = systems[component_name].add_component(self, entity_id, *args, **kwargs)
        self.entities[entity_id][component_index[component_name]] = index
    
    def destroy_entity(self, entity_id):
        try:
            for i, index in enumerate(self.entities[entity_id]):
                if index != -1:
                    system_index[i].remove_component(index)
            self.entities.pop(entity_id)
        except:
            pass

    def get_component(self, entity_id, component_name):
        try:
            component = systems[component_name].components[self.entities[entity_id][component_index[component_name]]]
            return component
        except KeyError:
            raise KeyError("Tried to get component that does not exist.")


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
        grid_box_w, grid_box_h = (GRID_SIZE, GRID_SIZE)

        left_buffer = -self.corner.x % grid_box_w
        for x in range(round(self.width // grid_box_w) + 1):
            x_pos = left_buffer + x * grid_box_w
            pygame.draw.line(game.screen, light_gray, (x_pos, 0), (x_pos, self.height))

        top_buffer = -self.corner.y % grid_box_h
        for y in range(round(self.height // grid_box_h) + 1):
            y_pos = top_buffer + y * grid_box_h
            pygame.draw.line(game.screen, light_gray, (0, y_pos), (self.width, y_pos))


def create_bullet(id, x, y, rotation, scale, owner, velocity, speed):
    game.create_entity(id)
    game.add_component(id, "transform", x, y, rotation, scale)
    game.add_component(id, "graphics", [(images[owner + "_bullet"], 0, 0)], game.get_component(id, "transform"))
    game.add_component(id, "physics", velocity, speed, 0.1, 0.05, game.get_component(id, "transform"))

def create_player(id, x, y, rotation, scale, speed, accel, friction):
    game.create_entity(id)
    game.add_component(id, "transform", x, y, rotation, scale)
    game.add_component(id, "graphics", [(images["barrel"], 0, 0), (images["player_body"], 0, 0)], game.get_component(id, "transform"))
    game.add_component(id, "physics", Vector2(0, 0), speed, accel, friction, game.get_component(id, "transform"))
    game.add_component(id, "controller", PlayerController(game, id, PLAYER_SPEED, PLAYER_ACCEL, game.get_component(id, "transform"), game.get_component(id, "physics")))
    game.add_component(id, "input handler", PlayerInputHandler(game, id, PLAYER_MOVE_KEYS))


if __name__ == "__main__":
    screen = pygame.display.set_mode(SCREEN_SIZE)

    game = Game(screen)
    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN])

    images.update(load_images())
    id = game.last_id
    create_player(id, 300, 300, 0, 1, PLAYER_SPEED, PLAYER_ACCEL, PLAYER_FRICTION)
    game.camera.set_target(id, True)

    while 1:
        '''elif event.type == MOUSEBUTTONDOWN:
            id = game.last_id
            velocity = Vector2(1, 0).rotate_ip(random.randrange(0, 360))
            speed = random.randint(5, 200)
            create_bullet(id, 300, 300, 0, 1, "player", velocity * speed)'''

        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time

        while game.accumulator >= game.dt:
            physics_sys.update(game.dt)
            game.camera.update()
            game.accumulator -= game.dt
        
        game.action_handler.get_player_input()
        game.action_handler.handle_actions()
        controller_sys.update()
        
        screen.fill(white)
        game.camera.draw_grid()
        graphics_sys.update(screen)
        pygame.display.update()