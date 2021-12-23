import pygame
import math
import time
import settings
from pygame.math import Vector2
from pygame.locals import *


class Component:
    def __init__(self, game, next_available):
        self.game = game
        self.next_available = next_available
        self.id = None
    def activate(self):
        pass


class Transform(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    def activate(self, id, x, y, rotation, scale):
        self.id = id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale


class Physics(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    def activate(self, id, angle, speeds, accel, decel, friction, transform_component):
        self.id = id
        self.max_speed, current_speed, target_speed = speeds
        self.accel = accel
        self.decel = decel
        self.friction = friction
        self.velocity = Vector2()
        self.velocity.from_polar((current_speed, angle))
        self.target_velocity = Vector2()
        self.target_velocity.from_polar((target_speed, angle))
        self.transform_component = transform_component


class Graphics(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    def activate(self, id, layer, images, transform_component):
        self.id = id
        self.layer = layer
        self.transform_component = transform_component
        # images = [(<name>, <offsetx>, <offsety>, <rotation>), (etc.)]
        self.images = images
        self.last_rotation = None
        self.last_used_images = [element[0] for element in self.images]


class Controller(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    def activate(self, id, controller_class):
        self.id = id
        self.controller_class = controller_class


class PlayerController:
    def __init__(self, game, id, move_keys, transform_component):
        self.game = game
        self.id = id
        self.move_keys = move_keys
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
                return action.Start_Firing_Barrels(self.id)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                return action.Stop_Firing_Barrels(self.id)


class Barrel_Manager(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    def activate(self, id, barrels, shooting, graphics_component, transform_component):
        self.id = id
        # barrels = [[scale, angle_offset, last_shot, cooldown, image_index], [<next barrel>]]
        # NOTE: reference each barrel in the order that they should be drawn
        self.barrels = barrels
        self.shooting = shooting
        self.graphics_component = graphics_component
        self.transform_component = transform_component


class System:
    def __init__(self, component_type):
        self.component_type = component_type
        self.components = []
        self.first_available = None
    
    def add_component(self, game, *args, **kwargs):
        if self.first_available is None:
            self.partition(game, 100)
        index = self.first_available
        self.components[index].activate(*args, **kwargs)
        self.first_available = self.components[index].next_available
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.first_available = index
        except:
            raise Exception("Unable to remove component.")
    
    def partition(self, game, amount):
        link = None
        new_comps = []
        for i in range(amount):
            comp = self.component_type(game, link)
            new_comps.insert(0, comp)
            if link is None:
                link = len(self.components) + amount - 1
            else:
                link -= 1
        self.first_available = len(self.components)
        self.components += new_comps
    
    def update(self):
        pass


class Transform_System(System):
    def __init__(self):
        super().__init__(Transform)


class Physics_System(System):
    def __init__(self):
        super().__init__(Physics)
    
    def update(self, dt):
        for component in self.components:
            if component.id is not None:
                if component.target_velocity == Vector2(0, 0):
                    component.velocity = component.velocity.lerp(component.target_velocity, component.decel * component.friction)
                else:
                    component.velocity = component.velocity.lerp(component.target_velocity, component.accel - component.accel * component.friction)

                component.transform_component.x += component.velocity.x * dt
                component.transform_component.y += component.velocity.y * dt


class Graphics_System(System):
    def __init__(self):
        super().__init__(Graphics)
        self.layer_indexes = []
        self.layers = 0
    
    def check_layer_exists(self, layer):
        """Instead of hardcoding the number of graphics layers that I will use, I let it create a new
        layer whenever a higher one is needed"""
        while self.layers < layer + 1:
            self.layer_indexes.append([])
            self.layers += 1
    
    def add_component(self, game, *args, **kwargs):
        layer = args[1]
        self.check_layer_exists(layer)
        if self.first_available is None:
            self.partition(game, 10)
        index = self.first_available
        self.components[index].activate(*args, **kwargs)
        self.first_available = self.components[index].next_available
        self.layer_indexes[layer].append(index)
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.layer_indexes[self.components[index].layer].remove(index)
            self.first_available = index
        except:
            raise Exception("Unable to remove component.")
    
    def update(self, screen):
        for layer in self.layer_indexes:
            for component_index in layer:
                component = self.components[component_index]
                if component.id is not None and Rect(component.game.camera.corner, (component.game.camera.width, component.game.camera.height)).collidepoint(component.transform_component.x, component.transform_component.y):
                    for index, element in enumerate(component.images):
                        image, offsetx, offsety, rotation_offset, scale_offset = element
                        if component.transform_component.rotation != component.last_rotation:
                            ck = image.get_colorkey()
                            width, height = image.get_size()
                            image = pygame.transform.scale(image, (math.ceil(width * component.transform_component.scale * scale_offset), math.ceil(height * component.transform_component.scale * scale_offset)))
                            image = pygame.transform.rotate(image, -component.transform_component.rotation - rotation_offset)
                            if ck:
                                image.set_colorkey(ck)
                            component.last_used_images[index] = image
                        width, height = component.last_used_images[index].get_size()
                        camera = component.game.camera
                        screen.blit(component.last_used_images[index], (component.transform_component.x - width // 2 + offsetx - camera.corner.x, component.transform_component.y - height // 2 + offsety - camera.corner.y))
                    component.last_rotation = component.transform_component.rotation


class Controller_System(System):
    def __init__(self):
        super().__init__(Controller)

    def update(self):
        for component in self.components:
            if component.id is not None:
                component.controller_class.update()
    
    def get_action_from_event(self, event):
        for component in self.components:
            if component.id is not None:
                action = component.controller_class.get_action(event)
                if action is not None:
                    component.game.add_action(action)


class Barrel_Manager_System(System):
    def __init__(self):
        super().__init__(Barrel_Manager)
    
    def update(self):
        for component in self.components:
            if component.id is not None:
                # update barrel animations?
                if component.shooting:
                    for barrel in component.barrels:
                        last_shot, cooldown, image_index = barrel
                        image, offset_x, offset_y, rotation_offset, scale_offset = component.graphics_component.images[image_index]
                        scale = component.transform_component.scale * scale_offset
                        if time.time() - last_shot >= cooldown:
                            barrel[0] = time.time()
                            barrel_length = settings.BARREL_LENGTH * scale
                            barrel_angle = component.transform_component.rotation + rotation_offset
                            barrel_end = Vector2()
                            barrel_end.from_polar((barrel_length, barrel_angle))
                            firing_point = Vector2(component.transform_component.x + offset_x, component.transform_component.y + offset_y) + barrel_end
                            id = component.game.get_unique_id() #                  id, spawn_point, rotation, scale, angle, speed, type, owner
                            component.game.add_action(component.game.actions.Spawn_Bullet(id, firing_point, 0, scale, barrel_angle, settings.PLAYER_MAX_SPEED + 10, "player"))


transform_sys = Transform_System()
physics_sys = Physics_System()
graphics_sys = Graphics_System()
controller_sys = Controller_System()
barrel_manager_sys = Barrel_Manager_System()

systems = {
    "transform":transform_sys,
    "physics":physics_sys,
    "graphics":graphics_sys,
    "controller":controller_sys,
    "barrel manager":barrel_manager_sys
}
component_index = {
    "transform":0,
    "physics":1,
    "graphics":2,
    "controller":3,
    "barrel manager":4
}
system_index = [transform_sys, physics_sys, graphics_sys, controller_sys, barrel_manager_sys]