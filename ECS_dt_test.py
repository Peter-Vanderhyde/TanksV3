import pygame
import sys
import random
import time
from pygame import transform
from pygame.locals import *
from pygame.math import Vector2
pygame.init()

font = pygame.font.Font('freesansbold.ttf', 25)

NUM_OF_COMPONENTS = 2

screen = pygame.display.set_mode((750, 750))

blue_ball = pygame.image.load("blue_ball.png").convert_alpha()
red_ball = pygame.image.load("red_ball.png").convert_alpha()
green_ball = pygame.image.load("green_ball.png").convert_alpha()
blue_square = pygame.image.load("blue_square.png").convert()
red_square = pygame.image.load("red_square.png").convert()
green_square = pygame.image.load("green_square.png").convert()

class Transform:
    def __init__(self, id, x, y, velocity, scale, bounce_percent):
        self.id = id
        self.x = x
        self.y = y
        self.velocity = velocity
        self.scale = scale
        self.bounce_percent = bounce_percent

class Graphics:
    def __init__(self, id, color, transform_component):
        self.id = id
        self.color = transform.scale(color, (transform_component.scale, transform_component.scale))
        self.transform_component = transform_component

class PhysicsSystem:
    def __init__(self):
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
        self.components[index] = Transform(*args, **kwargs)
        self.set_next_available()
        return index
    
    def remove_component(self, index):
        try:
            self.components[index] = None
        except:
            raise Exception("Unable to remove component.")
        
        if index < self.first_available:
            self.first_available = index
    
    def update(self, dt):
        destroy = []
        for component in self.components:
            if component != None:
                if gravity and (component.y != screen.get_height() or component.velocity.y != 0):
                    component.velocity.y += GRAVITY * dt
                if component.velocity.x != 0:
                    component.x += component.velocity.x * dt
                if component.velocity.y != 0: #  This addition saved 10 FPS when entities were flat on the ground
                    component.y += component.velocity.y * dt
                if BOUNCE:
                    if component.x < 0 and component.velocity.x < 0:
                        component.velocity.x *= -1
                    elif component.x > screen.get_width() and component.velocity.x > 0:
                        component.velocity.x *= -1
                    if component.y < 0 and component.velocity.y < 0:
                        component.velocity.y *= -1
                    elif component.velocity.y > 0 and component.y > screen.get_height():
                        if component.velocity.y < 10: #  This line made it runnable while gravity was on
                            component.velocity.y = 0
                        else:
                            component.velocity.y *= -1
                            component.velocity.y /= component.bounce_percent
                        component.y = screen.get_height()
        return destroy

class GraphicsSystem:
    def __init__(self):
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
        self.components[index] = Graphics(*args, **kwargs)
        self.set_next_available()
        return index
    
    def remove_component(self, index):
        try:
            self.components[index] = None
        except:
            raise Exception("Unable to remove component.")
        
        if index < self.first_available:
            self.first_available = index
    
    def update(self, screen):
        for component in self.components:
            if component != None:
                transform = component.transform_component
                scale = transform.scale
                if not BOUNCE:
                    if screen.get_rect().collidepoint((transform.x - scale // 2, transform.y - scale // 2)):
                        screen.blit(component.color, (transform.x - scale // 2, transform.y - scale // 2))
                else:
                    screen.blit(component.color, (transform.x - scale // 2, transform.y - scale // 2))

class EventHandler:
    def __init__(self):
        self.events = []
    
    def add_event(self, event):
        self.events.append(event)
    
    def handle_events(self):
        while self.events:
            self.events.pop(0).execute()

class Event:
    def execute(self):
        pass

class SetColor(Event):
    def __init__(self, color):
        self.color = color
    
    def execute(self):
        for component in graphics_system.components:
            if component != None:
                component.color = self.color

def add_component(entity_id, component_name, *args, **kwargs):
    index = systems[component_name].add_component(entity_id, *args, **kwargs)
    entities[entity_id][component_id[component_name]] = index

def create_entity(entity_id):
    component_indexes = [-1] * NUM_OF_COMPONENTS
    entities[entity_id] = component_indexes

def destroy_entity(entity_id):
    try:
        for i, index in enumerate(entities[entity_id]):
            if index != -1:
                system_index[i].remove_component(index)
        entities.pop(entity_id)
    except:
        pass

def get_component(entity_id, component_name):
    try:
        component = systems[component_name].components[entities[entity_id][component_id[component_name]]]
        return component
    except:
        raise Exception("Tried to get component that does not exist.")


if __name__ == "__main__":
    pygame.event.set_allowed([KEYDOWN])
    BOUNCE = True
    SPEED = 150
    GRAVITY = 1000
    MAX_ENTITIES = 5000
    gravity = False
    emit = True
    emition_rate = 1
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    colors = [green_ball, blue_ball, red_ball, green_square, red_square, blue_square]

    clock = pygame.time.Clock()

    event_handler = EventHandler()
    physics_system = PhysicsSystem()
    graphics_system = GraphicsSystem()

    systems = {
        "physics":physics_system,
        "graphics":graphics_system}
    system_index = [physics_system, graphics_system]
    component_id = {
        "physics":0,
        "graphics":1
    }

    next_id = 0
    last_id = 0
    living_entities = 0
    last_entity_count = living_entities
    chopping_block = []
    entities = {}

    dt = 0.01
    current_time = time.time()
    accumulator = 0.0

    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_r:
                    event_handler.add_event(SetColor(red_ball))
                elif event.key == K_b:
                    event_handler.add_event(SetColor(blue_ball))
                elif event.key == K_g:
                    event_handler.add_event(SetColor(green_ball))
                elif event.key == K_EQUALS:
                    MAX_ENTITIES += 500
                elif event.key == K_MINUS and MAX_ENTITIES != 500:
                    MAX_ENTITIES -= 500
                elif event.key == K_RETURN:
                    emit = not emit
                elif event.key == K_SPACE:
                    gravity = not gravity
                elif event.key == K_UP:
                    emition_rate += 1
                elif event.key == K_DOWN and emition_rate != 1:
                    emition_rate -= 1
        
        for entity_id in chopping_block:
            destroy_entity(entity_id)
            living_entities -= 1
        chopping_block = []
        
        while living_entities < MAX_ENTITIES and emit:
            for i in range(emition_rate):
                mouse_pos = pygame.mouse.get_pos()
                create_entity(next_id)
                velocity = Vector2(1, 1).normalize()
                velocity = velocity.rotate(random.randint(0, 360))
                velocity.scale_to_length(random.uniform(-SPEED, SPEED))
                add_component(next_id, "physics", mouse_pos[0], mouse_pos[1], velocity, random.randint(5, 10), random.uniform(1.2, 6.0))
                add_component(next_id, "graphics", random.choice(colors), get_component(next_id, "physics"))
                next_id += 1
                living_entities += 1

        while living_entities >= MAX_ENTITIES:
            destroy_entity(last_id)
            last_id += 1
            living_entities -= 1

        event_handler.handle_events()

        new_time = time.time()
        frame_time = new_time - current_time
        current_time = new_time

        accumulator += frame_time

        while accumulator >= dt:
            chopping_block.extend(physics_system.update(dt))
            accumulator -= dt
        
        screen.fill(white)
        graphics_system.update(screen)
        if last_entity_count != living_entities:
            surf = font.render(str(living_entities), 1, black)
            rect = surf.get_rect()
            rect.topleft = (0, 0)
            last_entity_count = living_entities
        screen.blit(surf, rect)
        surf2 = font.render(str(int(clock.get_fps())), 1, black)
        rect2 = surf2.get_rect()
        rect2.topright = (screen.get_width(), 0)
        screen.blit(surf2, rect2)
        pygame.display.update()
        clock.tick()