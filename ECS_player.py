import pygame
import sys
import time
import random
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


class Transform:
    def __init__(self, id, x, y, rotation, scale):
        self.id = id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale


class Physics:
    def __init__(self, id, velocity, transform_component):
        self.id = id
        self.velocity = velocity
        self.transform_component = transform_component


class Graphics:
    def __init__(self, id, image, transform_component):
        self.id = id
        self.transform_component = transform_component
        self.image = get_image(image, self.transform_component.scale)
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.last_rotation = self.transform_component.rotation
        self.last_used_image = self.image


class System:
    def __init__(self, component_type):
        self.component_type = component_type
        self.components = [None]
        self.first_available = 0
    
    def set_next_available(self):
        for index, component in enumerate(self.components[self.first_available:], self.first_available):
            if component == None:
                self.first_available = index
                return
        self.first_available = len(self.components)
        self.components.append(None)
    
    def add_component(self, *args, **kwargs):
        index = self.first_available
        self.components[index] = self.component_type(*args, **kwargs)
        self.set_next_available()
        return index
    
    def remove_component(self, index):
        try:
            self.components[index] = None
        except:
            raise Exception("Unable to remove component.")
        
        if index < self.first_available:
            self.first_available = index
    
    def update(self):
        pass


class TransformSystem(System):
    def __init__(self):
        super().__init__(Transform)


class PhysicsSystem(System):
    def __init__(self):
        super().__init__(Physics)
    
    def update(self, dt):
        for component in self.components:
            if component != None:
                component.transform_component.x += component.velocity.x * dt
                component.transform_component.y += component.velocity.y * dt


class GraphicsSystem(System):
    def __init__(self):
        super().__init__(Graphics)
    
    def update(self, screen):
        for component in self.components:
            if component != None:
                if component.last_rotation != component.transform_component.rotation:
                    component.last_rotation = component.transform_component.rotation
                    component.last_used_image = pygame.transform.rotate(component.image, component.last_rotation)
                screen.blit(component.last_used_image, (component.transform_component.x - component.image_width // 2, component.transform_component.y - component.image_height // 2))



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

    images = {}

    transform_sys = TransformSystem()
    physics_sys = PhysicsSystem()
    graphics_sys = GraphicsSystem()

    systems = {
        "transform":transform_sys,
        "physics":physics_sys,
        "graphics":graphics_sys
    }
    component_index = {
        "transform":0,
        "physics":1,
        "graphics":2
    }
    system_index = [transform_sys, physics_sys, graphics_sys]

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
        graphics_sys.update(screen)
        pygame.display.update()