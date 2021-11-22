import pygame
import sys
import time
import random
from components import *
from pygame.locals import *
from pygame.math import Vector2
pygame.init()


def load_image(path, alpha=True, colorkey=()):
    if alpha:
        image = pygame.image.load(path).convert_alpha()
        if colorkey != ():
            image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(path).convert()
    if image not in images:
        images[image] = {1:image}
    return image


def get_image(image, scale):
    if image in images:
        if scale in images[image]:
            return images[image][scale]
        else:
            new_image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
            if image.get_colorkey():
                new_image.set_colorkey(image.get_colorkey())
            images[image][scale] = new_image
            return new_image
    else:
        images[image] = {1:image}
        return image


class Game:
    def __init__(self, screen):
        self.screen = screen

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.entities = {}
        self.living_entities = 0

        self.user_input = []
    
    def create_entity(self, entity_id):
        component_indexes = [-1] * len(system_index)
        self.entities[entity_id] = component_indexes

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


class Event:
    def __init__(self, id=-1):
        self.id = id
    
    def execute(self):
        pass


class EventHandler:
    def __init__(self):
        self.events = []
    
    def add_event(self, event):
        self.events.append(event)
    
    def handle_events(self):
        while self.events:
            event = self.events.pop(0)
            if event.id == -1 or event.id in game.entities:
                event.execute()


class Quit(Event):
    def __init__(self, id=-1):
        super().__init__(id)
    
    def execute(self):
        pygame.quit()
        sys.exit()


def check_for_quit():
    for event in game.user_input:
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            event_handler.add_event(Quit())



if __name__ == "__main__":
    white = (255, 255, 255)
    black = (0, 0, 0)

    screen = pygame.display.set_mode((500, 500))
    game = Game(screen)
    event_handler = EventHandler()
    pygame.event.set_allowed([KEYDOWN])

    body = load_image("body.png", colorkey=white)

    game.create_entity(0)
    game.add_component(0, "transform", 250, 250, 0, 1)
    game.add_component(0, "graphics", body, game.get_component(0, "transform"))
    velocity = Vector2(0, 0)
    speed = random.randint(5, 200)
    game.add_component(0, "physics", velocity * speed, game.get_component(0, "transform"))

    while 1:
        game.user_input = pygame.event.get()
        check_for_quit()
        event_handler.handle_events()

        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time

        while game.accumulator >= game.dt:
            physics_sys.update(game.dt)
            game.accumulator -= game.dt
        
        screen.fill(white)
        pygame.draw.rect(screen, black, (200, 200, 30, 30))
        graphics_sys.update(screen)
        pygame.display.update()