import pygame
import math
import settings
from pygame.math import Vector2
from pygame.locals import *


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
    def __init__(self, game, id, angle, speeds, accel, friction, transform_component):
        super().__init__(game, id)
        self.max_speed, self.current_speed, self.target_speed = speeds
        self.accel = accel
        self.friction = friction
        self.velocity = Vector2()
        self.velocity.from_polar((self.current_speed, angle))
        self.target_velocity = Vector2()
        self.target_velocity.from_polar((self.target_speed, angle))
        self.transform_component = transform_component


class Graphics(Component):
    def __init__(self, game, id, images, transform_component):
        super().__init__(game, id)
        self.transform_component = transform_component
        # [(<name>, <offsetx>, <offsety>), (etc.)]
        self.images = images
        self.last_rotation = None
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
        action = self.game.actions
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                return action.Quit()
            elif event.key == self.move_keys["left"]:
                return action.MoveLeft(self.id, True)
            elif event.key == self.move_keys["right"]:
                return action.MoveRight(self.id, True)
            elif event.key == self.move_keys["up"]:
                return action.MoveUp(self.id, True)
            elif event.key == self.move_keys["down"]:
                return action.MoveDown(self.id, True)
        elif event.type == KEYUP:
            if event.key == self.move_keys["left"]:
                return action.MoveLeft(self.id, False)
            elif event.key == self.move_keys["right"]:
                return action.MoveRight(self.id, False)
            elif event.key == self.move_keys["up"]:
                return action.MoveUp(self.id, False)
            elif event.key == self.move_keys["down"]:
                return action.MoveDown(self.id, False)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                id = self.game.last_id
                self.game.last_id += 1
                transform = self.game.get_component(self.id, "transform")
                return action.Shoot(id, Vector2(transform.x, transform.y), 0, 1, transform.rotation, settings.PLAYER_MAX_SPEED, "bullet", "player")


class Controller(Component):
    def __init__(self, game, id, controller_class):
        super().__init__(game, id)
        self.controller_class = controller_class


class PlayerController(Component):
    def __init__(self, game, id, transform_component):
        super().__init__(game, id)
        self.transform_component = transform_component
        self.velx = 0
        self.vely = 0
    
    def update(self):
        transform = self.transform_component
        distance_between = (pygame.mouse.get_pos() + self.game.camera.corner) - Vector2(transform.x, transform.y)
        angle = distance_between.as_polar()[1]
        transform.rotation = angle

        physics = self.game.get_component(self.id, "physics")
        physics.target_velocity = Vector2(self.velx, self.vely)
        if (self.velx, self.vely) != (0, 0):
            physics.target_velocity.scale_to_length(physics.max_speed)


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
                if component.target_velocity == Vector2(0, 0):
                    component.velocity = component.velocity.lerp(component.target_velocity, component.friction)
                else:
                    component.velocity = component.velocity.lerp(component.target_velocity, component.accel - component.friction)

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
                        ck = image.get_colorkey()
                        width, height = image.get_size()
                        image = pygame.transform.scale(image, (math.ceil(width * component.transform_component.scale), math.ceil(height * component.transform_component.scale)))
                        image = pygame.transform.rotate(image, -component.transform_component.rotation)
                        if ck:
                            image.set_colorkey(ck)
                        component.last_used_images[index] = image
                    width, height = component.last_used_images[index].get_size()
                    camera = component.game.camera
                    screen.blit(component.last_used_images[index], (component.transform_component.x - width // 2 + offsetx - camera.corner.x, component.transform_component.y - height // 2 + offsety - camera.corner.y))
                component.last_rotation = component.transform_component.rotation


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
    
    def create_player_action(self, event):
        for component in self.components:
            if component is not None:
                if isinstance(component.input_class, PlayerInputHandler):
                    action = component.input_class.get_action(event)
                    if action is not None:
                        component.game.add_action(action)
    
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