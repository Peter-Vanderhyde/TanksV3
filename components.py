import pygame
import math
import time
import settings
import numpy as np
from pygame.math import Vector2
from pygame.locals import *

'''
-----------
DEFINITIONS
-----------
(Use <component>.activate? to see args)

Transform: (x, y, rotation, scale)
Physics: (angle, speeds: [<max_speed>, <current_speed>, <target_speed>], rotational_force, acceleration, deceleration, friction, transform_component, rotational_friction=True)
Graphics: (layer-(0 is the bottom layer), images: [(<name>, <offset_position>, <rotation>, <scale_offset>), (etc.)], transform_component)
Controller: (controller_class)
Enemy_Controller: (TBD)
Player_Controller: (move_keys: {'left':<key>, 'right':..., 'up':..., 'down':...}, transform_component)
Barrel_Manager: (barrels: [[<last_shot>, <cooldown>, <image_index>], [etc.]], shooting, owner_string, graphics_component, transform_component)
Life_Timer: (start_time, duration)
Collider: (collision_id, radius, offset, collision_category, collidable_categories: ['actors', 'projectiles', 'shapes'], transform_component)

'''


class Component:

    def __init__(self, game, next_available):
        self.game = game
        self.next_available = next_available
        self.id = None
    
    def activate(self):
        """Any information needed by the class is given when the inactive component is 'activated'"""

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
    
    def activate(self, id, angle, speeds, rotational_force, accel, decel, friction, transform_component, rotation_friction=True):
        self.id = id
        self.max_speed, current_speed, target_speed = speeds
        self.rotational_force = rotational_force
        self.accel = accel
        self.decel = decel
        self.friction = friction
        self.velocity = Vector2()
        self.velocity.from_polar((current_speed, angle))
        self.target_velocity = Vector2()
        self.target_velocity.from_polar((target_speed, angle))
        self.transform_component = transform_component
        self.rotation_friction = rotation_friction

class Graphics(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, layer, images, transform_component):
        self.id = id
        self.layer = layer
        self.transform_component = transform_component
        # images = [[<name>, <offset_position>, <rotation>, <scale_offset>], [etc.]]
        self.images = images
        self.last_rotation = None
        self.last_used_images = [element[0] for element in self.images]
        self.previous_images = [element[0] for element in self.images]
    
    def switch_image_frame(self, index, new_image):
        self.images[index][0] = new_image

class Controller(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, controller_name, *args):
        self.id = id
        self.controller_name = controller_name
        self.controller_class = self.game.controllers.name_dict[controller_name](self.game, self.id, *args)

class BarrelManager(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, barrels, shooting, projectile_name, graphics_component, transform_component, animator_component):
        self.id = id
        # barrels = [[last_shot, cooldown, image_index], [<next barrel>]]
        # NOTE: reference each barrel in the order that they should be drawn
        self.barrels = barrels
        self.shooting = shooting
        self.projectile_name = projectile_name
        self.graphics_component = graphics_component
        self.transform_component = transform_component
        self.animator_component = animator_component

class LifeTimer(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, start_time, duration):
        self.id = id
        self.start_time = start_time
        self.duration = duration

class Collider(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, collision_id, radius, offset, collision_category, collidable_categories, particle_source_name, transform_component):
        self.id = id
        self.collision_id = collision_id
        # This is the id of the actual parent entity this collider is connected
        # to. This allows easy reference when collisions are detected for changing
        # health, experience, etc.
        self.radius = radius
        self.offset = offset
        self.collision_category = collision_category
        # The category that this collider component falls under.
        # It can only have one.
        self.collidable_categories = collidable_categories
        # This is a list of all of the collision categories that this collider can collide
        # with. Any colliders not under these categories will be ignored when checking collisions
        self.particle_source_name = particle_source_name
        self.transform_component = transform_component
        self.collision_cells = set()

class HealthBar(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, width, height, offset, transform_component):
        self.id = id
        self.width = width
        self.height = height
        self.offset = offset
        self.transform_component = transform_component

class Animator(Component):
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, animation_set, current_animations, graphics_component):
        self.id = id
        self.animation_set = ""
        self.current_animations = []
        self.animation_states = []
        self.graphics_component = graphics_component
        self.current_frame = None
        self.start_time = None
        self.frame_start_time = None
        self.images = {}
        self.set_animation_set(animation_set)
        for animation in current_animations:
            self.add_animation_state(animation)
    
    def add_animation_state(self, animation):
        if animation in self.current_animations:
            self.stop(animation)
        self.current_animations.append(animation)
        self.animation_states.append({
            "animation":animation,
            "current_frame":None,
            "start_time":None,
            "frame_start_time":None
        })
    
    def get_state_of_animation(self, animation):
        """Gives you the animation, current_frame, start_time, and frame_start_time of an animation"""

        try:
            index = self.current_animations.index[animation]
            return self.animation_states[index]
        except ValueError:
            raise ValueError("Tried to get state of animation not in Animator!")
    
    def set_animation_set(self, animation_set):
        self.animation_set = animation_set
        self.images = {}
        for index, name in enumerate(self.game.animations[animation_set]["indexes"]):
            self.images.update({name:index})
        self.current_animations = []
        self.animation_states = []
    
    def play(self, animation):
        self.add_animation_state(animation)
    
    def stop(self, animation):
        index = self.current_animations.index(animation)
        self.current_animations.remove(animation)
        self.animation_states.pop(index)

class System:
    def __init__(self, component_type):
        self.component_type = component_type
        self.components = []
        self.first_available = None
        self.farthest_component = 0
    
    def add_component(self, game, *args, **kwargs):
        if self.first_available is None:
            self.partition(game, max(len(self.components) + 1, 10)) # Partitions at least 10 empty spaces, but otherwise doubles the size
        index = self.first_available
        self.components[index].activate(*args, **kwargs)
        self.first_available = self.components[index].next_available
        if index > self.farthest_component:
            self.farthest_component = index
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.first_available = index
            if index == self.farthest_component:
                while index - 1 >=0 and self.components[index - 1].id is None:
                    index -= 1
                self.farthest_component = index
        except:
            raise Exception("Unable to remove component.")
    
    def partition(self, game, amount):
        link = None
        new_comps = []
        insert = new_comps.insert
        length = len(self.components)
        for i in range(amount):
            comp = self.component_type(game, link)
            insert(0, comp)
            if link is None:
                link = length + amount - 1
            else:
                link -= 1
        self.first_available = length
        self.components += new_comps
    
    def update(self):
        """Contains whatever code should be run for that component every loop"""
        pass

class TransformSystem(System):
    def __init__(self):
        super().__init__(Transform)

class PhysicsSystem(System):
    def __init__(self):
        super().__init__(Physics)
    
    def update(self, dt):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                if component.target_velocity == Vector2(0, 0):
                    component.velocity = component.velocity.lerp(component.target_velocity, component.decel * component.friction)
                else:
                    component.velocity = component.velocity.lerp(component.target_velocity, component.accel - component.accel * component.friction)

                component.transform_component.x += component.velocity.x * dt
                component.transform_component.y += component.velocity.y * dt

                component.transform_component.rotation += component.rotational_force * 10 * dt
                if component.rotation_friction and component.rotational_force:
                    v = Vector2(1, 0) * component.rotational_force
                    v = v.lerp(Vector2(), min(component.rotational_force * 0.05 * dt, 0.05))
                    component.rotational_force = v.length()

class GraphicsSystem(System):
    def __init__(self):
        super().__init__(Graphics)
        self.layer_indexes = []
        self.layers = 0
    
    def check_layer_exists(self, layer):
        """Instead of hardcoding the number of graphics layers that I will use, I let it create a new
        layer whenever a higher one is needed. 0 is the bottom layer."""

        while self.layers < layer + 1:
            self.layer_indexes.append([])
            self.layers += 1
    
    def add_component(self, game, *args, **kwargs):
        layer = args[1]
        self.check_layer_exists(layer)
        if self.first_available is None:
            self.partition(game, max(len(self.components) + 1, 10))
        index = self.first_available
        self.components[index].activate(*args, **kwargs)
        self.first_available = self.components[index].next_available
        self.layer_indexes[layer].append(index)
        if index > self.farthest_component:
            self.farthest_component = index
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.layer_indexes[self.components[index].layer].remove(index)
            self.first_available = index
            if index == self.farthest_component:
                while index - 1 >=0 and self.components[index - 1].id is None:
                    index -= 1
                self.farthest_component = index
        except:
            raise Exception("Unable to remove component.")
    
    def update(self):
        for layer in self.layer_indexes:
            for component_index in layer:
                component = self.components[component_index]
                if component.id is not None and Rect(component.game.camera.corner, (component.game.camera.width, component.game.camera.height)).collidepoint(component.transform_component.x, component.transform_component.y):
                    for index, element in enumerate(component.images):
                        image, offset_vector, rotation_offset, scale_offset = element
                        if component.transform_component.rotation != component.last_rotation or component.images[index][0] != component.previous_images[index]:
                            ck = image.get_colorkey()
                            width, height = image.get_size()
                            image = pygame.transform.scale(image, (math.ceil(width * component.transform_component.scale * scale_offset), math.ceil(height * component.transform_component.scale * scale_offset)))
                            image = pygame.transform.rotate(image, -component.transform_component.rotation - rotation_offset)
                            if ck:
                                image.set_colorkey(ck)
                            component.last_used_images[index] = image
                            component.previous_images[index] = component.images[index][0]
                        width, height = component.last_used_images[index].get_size()
                        camera = component.game.camera
                        offset_x, offset_y = offset_vector.rotate(component.transform_component.rotation)
                        component.game.screen.blit(component.last_used_images[index], (component.transform_component.x - width // 2 + offset_x - camera.corner.x, component.transform_component.y - height // 2 + offset_y - camera.corner.y))
                    component.last_rotation = component.transform_component.rotation

class ControllerSystem(System):
    def __init__(self):
        super().__init__(Controller)

    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                component.controller_class.update()
    
    def get_action_from_event(self, event):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                action = component.controller_class.get_action(event)
                if action is not None:
                    component.game.add_action(action)

class BarrelManagerSystem(System):
    def __init__(self):
        super().__init__(BarrelManager)
    
    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                # update barrel animations?
                if component.shooting:
                    for barrel in component.barrels:
                        last_shot, cooldown, image_index = barrel
                        image, offset_vector, rotation_offset, scale_offset = component.graphics_component.images[image_index]
                        scale = component.transform_component.scale * scale_offset
                        if time.time() - last_shot >= cooldown:
                            barrel[0] = time.time()
                            barrel_length = settings.BARREL_LENGTH - 10 * scale
                            barrel_angle = component.transform_component.rotation + rotation_offset
                            barrel_end = Vector2()
                            barrel_end.from_polar((barrel_length, barrel_angle))
                            offset_x, offset_y = offset_vector.rotate(component.transform_component.rotation)
                            firing_point = Vector2(component.transform_component.x + offset_x, component.transform_component.y + offset_y) + barrel_end
                            id = component.game.get_unique_id() #                         id, spawn_point, rotation, scale, angle, speed, owner
                            component.game.add_action(component.game.actions.SpawnBullet(id, component.id, firing_point, component.transform_component.rotation, scale, barrel_angle, settings.PLAYER_MAX_SPEED + 10, component.projectile_name))
                            component.animator_component.play("shoot barrel")

class LifeTimerSystem(System):
    def __init__(self):
        super().__init__(LifeTimer)
    
    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                if time.time() - component.start_time >= component.duration:
                    component.game.add_action(component.game.actions.Destroy(component.id))

class ColliderSystem(System):
    def __init__(self):
        super().__init__(Collider)
    
    def add_component(self, game, *args, **kwargs):
        index = super().add_component(game, *args, **kwargs)
        self.components[index].game.collision_maps[self.components[index].collision_category].insert_collider(self.components[index])
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].game.collision_maps[self.components[index].collision_category].remove_collider(self.components[index])
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.first_available = index
            if index == self.farthest_component:
                while index - 1 >=0 and self.components[index - 1].id is None:
                    index -= 1
                self.farthest_component = index
        except:
            raise Exception("Unable to remove component.")
    
    def distance_between(self, a, b):
        return math.sqrt((b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y))

    def distance_between_squared(self, a, b):
        return (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y)

    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                component.game.collision_maps[component.collision_category].move_collider(component)
        
        # THIS IS A HORRID FUNCTION
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                game = component.game
                transform = component.transform_component
                origin = Vector2(transform.x, transform.y) + component.offset
                colliding_with_set = set().union(*[game.collision_maps[c].contents.get(cell)
                        for cell in component.collision_cells for c in component.collidable_categories
                        if game.collision_maps[c].contents.get(cell) != None])
                # These for loops loop through the categories that the collider is colliding with
                # and gets the cells of each, ignoring any that are empty (ie None).
                # It combines the cell sets of all the dictionaries that are in the same cell as itself.
                colliding_with_set -= {component}
                # Removes itself from the set so it doesn't collide with itself.
                for other_collider in colliding_with_set:
                    other_transform = other_collider.transform_component
                    other_origin = Vector2(other_transform.x, other_transform.y) + other_collider.offset
                    if component.collision_id != other_collider.collision_id and self.distance_between_squared(origin, other_origin) < (component.radius + other_collider.radius) ** 2:
                        game.helpers.handle_collision(component, other_collider)
                        # Checks what the categories are of the colliding objects, and acts accordingly.

class HealthBarSystem(System):
    def __init__(self):
        super().__init__(HealthBar)
    
    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                game = component.game
                transform = component.transform_component
                rect = Rect(0, 0, component.width, component.height)
                rect.center = (transform.x + component.offset.x - game.camera.corner.x,
                    transform.y + component.offset.y - game.camera.corner.y)
                health = game.get_property(component.id, "health")
                max_health = game.get_property(component.id, "max health")
                if health < max_health:
                    p = health / max_health
                    width = p * component.width
                    pygame.draw.rect(game.screen, game.colors.black, rect, 0, 2)
                    width = p * (component.width - 2)
                    pygame.draw.rect(game.screen, game.colors.green, ((rect.topleft[0] + 1, rect.topleft[1] + 1), (width, component.height - 2)), 0, 2)

class AnimatorSystem(System):
    def __init__(self):
        super().__init__(Animator)
    
    def update(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                game = component.game
                anim_set = component.animation_set
                for current_animation, animation_state in zip(component.current_animations, component.animation_states):
                    animation_properties = game.animations[anim_set][current_animation]
                    duration = animation_properties["duration"]
                    state = animation_state
                    if state["start_time"] == None:
                        state["start_time"] = time.time()
                        state["frame_start_time"] = time.time()
                        state["current_frame"] = 0
                        self.apply_frame(component, state, animation_properties["initial_frame"])
                        if duration == 0:
                            self.end_animation(component, state, animation_properties["loop"])
                    elif duration > 0:
                        frame = animation_properties["frames"][state["current_frame"]]
                        frame_duration = duration * frame["delay"]
                        elapsed = time.time() - state["frame_start_time"]
                        if time.time() - state["start_time"] >= duration:
                            self.apply_frame(component, state, animation_properties["frames"][-1]["properties"])
                            self.end_animation(component, state, animation_properties["loop"])
                            continue
                        elif elapsed >= frame_duration:
                            if self.go_to_next_frame(component, state, animation_properties, frame, frame_duration, elapsed):
                                frame = animation_properties["frames"][state["current_frame"]]
                                frame_duration = duration * frame["delay"]
                                elapsed = time.time() - state["frame_start_time"]
                                if time.time() - state["start_time"] >= duration:
                                    self.apply_frame(component, state, animation_properties["frames"][-1]["properties"])
                                    self.end_animation(component, state, animation_properties["loop"])
                                    continue
                            else:
                                continue
                        
                        elapsed_percent = elapsed / frame_duration
                        self.iterate_frame(component, frame, elapsed_percent)
    
    def apply_frame(self, component, state, frame):
        graphics = component.graphics_component
        images = component.images
        for image, properties in frame.items():
            for property, value in properties.items():
                if property == "image":
                    name = "/".join([component.animation_set, state["animation"], image])
                    graphics.switch_image_frame(images[image], component.game.animation_images[f"{name}_{value}"])

    def iterate_frame(self, component, frame, percent):
        pass

    def go_to_next_frame(self, component, state, animation_properties, frame, frame_duration, elapsed):
        self.apply_frame(component, state, frame["properties"])
        if state["current_frame"] + 1 == len(animation_properties["frames"]):
            self.end_animation(component, state)
            return False
        else:
            past = elapsed - frame_duration
            state["current_frame"] += 1
            state["frame_start_time"] = time.time() - past
            return True
    
    def end_animation(self, component, state, loop):
        if not loop:
            component.current_animations.remove(state["animation"])
            component.animation_states.remove(state)
        else:
            state["start_time"] = None


transform_sys = TransformSystem()
physics_sys = PhysicsSystem()
graphics_sys = GraphicsSystem()
controller_sys = ControllerSystem()
barrel_manager_sys = BarrelManagerSystem()
life_timer_sys = LifeTimerSystem()
collider_sys = ColliderSystem()
health_bar_sys = HealthBarSystem()
animator_sys = AnimatorSystem()

systems = {
    "transform":transform_sys,
    "physics":physics_sys,
    "graphics":graphics_sys,
    "controller":controller_sys,
    "barrel manager":barrel_manager_sys,
    "life timer":life_timer_sys,
    "collider":collider_sys,
    "health bar":health_bar_sys,
    "animator":animator_sys
}
component_index = {}
# Maps components to the index they are stored at in the entities. ie{"transform":0,"physics":1}

for i, component in enumerate(systems):
    component_index[component] = i

system_index = [s for s in systems.values()]