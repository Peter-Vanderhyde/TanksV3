import pygame
from pygame.math import Vector2
from pygame.locals import *
from actions import *


class Component:
    def __init__(self, game, id):
        self.game = game
        self.id = id


class Transform(Component):
    def __init__(self, game, id, x, y, rotation, scale):
        super().__init__(game, id)
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale


class Physics(Component):
    def __init__(self, game, id, velocity, transform_component):
        super().__init__(game, id)
        self.velocity = velocity
        self.transform_component = transform_component


class Graphics(Component):
    def __init__(self, game, id, images, transform_component):
        super().__init__(game, id)
        self.transform_component = transform_component
        # [(<name>, <offsetx>, <offsety>), (etc.)]
        self.images = images
        self.last_rotation = 0
        self.last_used_images = [element[0] for element in self.images]


class InputHandler(Component):
    def __init__(self, game, id, input_class):
        super().__init__(game, id)
        self.input_class = input_class


class PlayerInputHandler(Component):
    def __init__(self, game, id, move_keys):
        super().__init__(game, id)
        self.move_keys = move_keys
    
    def get_action(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return Quit()
            if event.key == self.move_keys["left"]:
                return MoveLeft(self.id, Vector2(-1, 0) * 100, 0.1, self.game.get_component(self.id, "physics"))


class Controller(Component):
    def __init__(self, game, id, controller_class):
        super().__init__(game, id)
        self.controller_class = controller_class


class PlayerController(Component):
    def __init__(self, game, id, max_velocity, acceleration, transform_component, physics_component):
        super().__init__(game, id)
        self.max_velocity = max_velocity
        self.acceleration = acceleration
        self.transform_component = transform_component
        self.physics_component = physics_component
    
    def update(self):
        transform = self.transform_component
        distance_between = pygame.mouse.get_pos() - Vector2(transform.x, transform.y)
        angle = distance_between.as_polar()[1]
        transform.rotation = -angle


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
    
    def add_component(self, game, *args, **kwargs):
        index = self.first_available
        self.components[index] = self.component_type(game, *args, **kwargs)
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
            if component is not None:
                component.transform_component.x += component.velocity.x * dt
                component.transform_component.y += component.velocity.y * dt


class GraphicsSystem(System):
    def __init__(self):
        super().__init__(Graphics)
    
    def update(self, screen):
        for component in self.components:
            if component is not None:
                for index, element in enumerate(component.images):
                    image, offsetx, offsety = element
                    if component.transform_component.rotation != component.last_rotation:
                        component.last_rotation = component.transform_component.rotation
                        ck = image.get_colorkey()
                        image = pygame.transform.rotate(image, component.transform_component.rotation)
                        if ck:
                            image.set_colorkey(ck)
                        component.last_used_images[index] = image
                    width, height = component.last_used_images[index].get_size()
                    screen.blit(component.last_used_images[index], (component.transform_component.x - width // 2 + offsetx, component.transform_component.y - height // 2 + offsety))


class ControllerSystem(System):
    def __init__(self):
        super().__init__(Controller)

    def update(self):
        for component in self.components:
            if component is not None:
                component.controller_class.update()


class InputHandlerSystem(System):
    def __init__(self):
        super().__init__(InputHandler)
    
    def create_player_action(self, event, handler):
        for component in self.components:
            if component is not None:
                if isinstance(component.input_class, PlayerInputHandler):
                    action = component.input_class.get_action(event)
                    if action is not None:
                        handler.add_action(action)
    
    def update(self):
        for component in self.components:
            if component is not None:
                component.event_class.update()


transform_sys = TransformSystem()
physics_sys = PhysicsSystem()
graphics_sys = GraphicsSystem()
controller_sys = ControllerSystem()
input_handler_sys = InputHandlerSystem()

systems = {
    "transform":transform_sys,
    "physics":physics_sys,
    "graphics":graphics_sys,
    "controller":controller_sys,
    "input handler":input_handler_sys
}
component_index = {
    "transform":0,
    "physics":1,
    "graphics":2,
    "controller":3,
    "input handler":4
}
system_index = [transform_sys, physics_sys, graphics_sys, controller_sys, input_handler_sys]