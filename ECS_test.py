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

def quit():
    pygame.quit()
    sys.exit()

class Game:
    def __init__(self, screen):
        self.screen = screen

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.entities = {}
        self.living_entities = 0
        self.last_id = 0

        self.action_handler = ActionHandler(input_handler_sys)
    
    def create_entity(self, entity_id):
        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(system_index)
        # Each entity is just this list of component indexes associated with an id key
        self.entities[entity_id] = component_indexes
        self.last_id += 1

    def add_component(self, entity_id, component_name, *args, **kwargs):
        index = systems[component_name].add_component(entity_id, *args, **kwargs)
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
        except:
            raise Exception("Tried to get component that does not exist.")


def create_bullet(id, x, y, rotation, scale, owner, velocity):
    game.create_entity(id)
    game.add_component(id, "transform", x, y, rotation, scale)
    game.add_component(id, "graphics", [(images[owner + "_bullet"], 0, 0)], game.get_component(id, "transform"))
    game.add_component(id, "physics", velocity, game.get_component(id, "transform"))

def create_player(id, x, y, rotation, scale, velocity):
    game.create_entity(id)
    game.add_component(id, "transform", x, y, rotation, scale)
    game.add_component(id, "graphics", [(images["barrel"], 0, 0), (images["player_body"], 0, 0)], game.get_component(id, "transform"))
    game.add_component(id, "physics", velocity, game.get_component(id, "transform"))
    game.add_component(id, "controller", PlayerController(id, PLAYER_SPEED, PLAYER_ACCEL, game.get_component(id, "transform"), game.get_component(id, "physics")))
    game.add_component(id, "input handler", PlayerInputHandler(id))


if __name__ == "__main__":
    screen = pygame.display.set_mode(RESOLUTION)

    game = Game(screen)
    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN])

    images.update(load_images())
    create_player(game.last_id, 300, 300, 0, 1, Vector2(0, 0))

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
            game.accumulator -= game.dt
        
        game.action_handler.get_player_input()
        game.action_handler.handle_actions()
        controller_sys.update()
        
        screen.fill(black)
        pygame.draw.rect(screen, black, (200, 200, 30, 30))
        graphics_sys.update(screen)
        pygame.display.update()