import pygame
from pygame.math import Vector2


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
    def __init__(self, id, images, transform_component):
        self.id = id
        self.transform_component = transform_component
        # [(<name>, <offsetx>, <offsety>), (etc.)]
        self.images = images
        self.last_rotation = 0
        self.last_used_images = [element[0] for element in self.images]


class Controller:
    def __init__(self, id, controller_class):
        self.id = id
        self.controller_class = controller_class


class PlayerController:
    def __init__(self, id, transform_component):
        self.id = id
        self.transform_component = transform_component
    
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


transform_sys = TransformSystem()
physics_sys = PhysicsSystem()
graphics_sys = GraphicsSystem()
controller_sys = ControllerSystem()

systems = {
    "transform":transform_sys,
    "physics":physics_sys,
    "graphics":graphics_sys,
    "controller":controller_sys
}
component_index = {
    "transform":0,
    "physics":1,
    "graphics":2,
    "controller":3
}
system_index = [transform_sys, physics_sys, graphics_sys, controller_sys]