import pygame
import math
import time
import settings
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
EnemyController: (TBD)
PlayerController: (move_keys: {'left':<key>, 'right':..., 'up':..., 'down':...}, transform_component)
BarrelManager: (barrels: [[<last_shot>, <cooldown>, <image_index>], [etc.]], shooting, owner_string, graphics_component, transform_component)
LifeTimer: (start_time, duration)
Collider: (parent_id, radius, offset, collision_category, collidable_categories: ['actors', 'projectiles', 'shapes', 'particles], transform_component)
HealthBar
Animator
UI

'''


class Component:
    """
    The base function that all components use. A component is stored in a list of components of the
    same type of component. It keeps track of the next unused component for easy reference.
    """

    def __init__(self, game, next_available):
        self.game = game
        # A reference to what is the next nearest unused component in the list of components
        self.next_available = next_available
        self.id = None
    
    def activate(self):
        """Any information needed by the class is given when the inactive component is 'activated'"""

        pass

class Transform(Component):
    """
    This component stores the x, y, rotation, and scale information of an entity.
    """

    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, x, y, rotation, scale):
        self.id = id
        self._pos = Vector2(x, y)
        self._x = self.pos.x
        self._y = self.pos.y
        self.rotation = rotation
        self.scale = scale
    
    # The followinig functions allow pos, x, and y to all be
    # connected so they each update each other and return the
    # same values
    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self._x = value.x
        self._y = value.y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self._pos.x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._pos.y = value

class Physics(Component):
    """
    This component keeps track of an entity's max speed, rotational force, acceleration speed,
    deceleration speed, friction, current velocity, target velocity, rotation friction, and a
    reference to a transform component.
    """

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
    """
    This component handles the different images the entity is composed of and updating said images.
    It keeps track of what layer the entity is drawn on as well (0 is the farthest back).
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, layer, images_info, transform_component):
        self.id = id
        self.layer = layer
        self.transform_component = transform_component
        # images_info = [{"image", "position offset", "rotation offset", "scale offset"}, {etc.}]
        # The offsets are the values applied after the entity's own properties are applied
        # i.e. the image is rotated however much the entity is rotated and then rotated more based on its offset
        self.images_info = images_info
        # This keeps track of the last rotation and scale of the parent entity
        # so the pieces can update appropriately
        self.last_entity_props = {
            "rotation":self.transform_component.rotation,
            "scale":self.transform_component.scale
        }
        # The image_mods keep track of edits made to the individual images by things
        # like the animation component
        self.image_mods = [{}] * len(images_info)
        self.reset_mods(list(range(len(images_info))))
        # Make a list of images that can be modified
        self.modifiable_images = [image_info["image"] for image_info in self.images_info]
    
    def reset_mods(self, indexes):
        for index in indexes:
            # Each property keeps track of the current value and the last value in case of changes
            image = self.images_info[index]["image"]
            self.image_mods[index] = {
                                    "redraw":True,
                                    "image":{"current":image, "previous":None},
                                    "position":{"current":Vector2(0, 0), "previous":Vector2(0, 0)},
                                    "rotation":{"current":0, "previous":0},
                                    "scale":{"current":1, "previous":1}
                                    }

    def set_image(self, index, new_image):
        """
        This exchanges an image that was being used for this piece of the sprite for a different one
        """
        
        self.images_info[index]["image"] = new_image
        self.set_image_property(index, "name", new_image)
    
    def set_image_property(self, image_index, image_property, value, set_current=False, set_previous=False):
        property = self.image_mods[image_index][image_property]
        if set_current:
            property["current"] = value
            if value != property["previous"]:
                self.image_mods[image_index]["redraw"] = True
        elif set_previous:
            property["previous"] = value
            if value != property["current"]:
                self.image_mods[image_index]["redraw"] = True
        else:
            if value != property["previous"]:
                self.image_mods[image_index]["redraw"] = True
            property.update({"current":value, "previous":property["current"]})
    
    def get_image_property(self, image_index, image_property, get_previous=False):
        if get_previous:
            return self.image_mods[image_index][image_property]["previous"]
        else:
            return self.image_mods[image_index][image_property]["current"]
    
    def update_image(self, index):
        self.image_mods[index]["redraw"] = False
    
    def image_properties_were_updated(self, index):
        return self.image_mods[index]["redraw"]
    
    def image_property_was_updated(self, index, property):
        property = self.image_mods[index][property]
        return property["current"] != property["previous"]
    
    def image_was_changed(self, index):
        return self.image_property_was_updated(index, "image")
    
    def entity_was_updated(self):
        transform = self.transform_component
        if [transform.rotation, transform.scale] != self.last_entity_props.values():
            self.last_entity_props.update({"rotation":transform.rotation, "scale":transform.scale})
            return True
        return False

class Controller(Component):
    """
    This class uses the PlayerController and EnemyController classes to update the movement and
    behavior of entities.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, controller_name, *args):
        self.id = id
        self.controller_name = controller_name
        # Sets its class based on if Player Controller or Enemy Controller was passed in
        self.controller_class = self.game.controllers.name_dict[controller_name](self.game, self.id, *args)

class BarrelManager(Component):
    """
    This handles the barrels of entities to affect when they shoot, their cooldown, a reference
    to the image being used for them, etc.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, barrels, shooting, projectile_name, graphics_component, transform_component, animator_component):
        self.id = id
        # barrels = [[cooldown, image_index], [<next barrel>]]
        # NOTE: reference each barrel in the order that they should be drawn
        self.barrels = barrels
        for barrel in self.barrels:
            # Becomes [accumulated_time_since_last_shot, cooldown, image_imdex]
            barrel.insert(0, 0)
        
        self.shooting = shooting
        self.projectile_name = projectile_name
        self.graphics_component = graphics_component
        self.transform_component = transform_component
        self.animator_component = animator_component

class LifeTimer(Component):
    """
    This component is for entities with a set lifetime so that it can be
    destroyed after that length of time.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, duration, animator_component=None):
        self.id = id
        self.duration = duration
        self.accumulated = 0
        self.animator_component = animator_component

class Collider(Component):
    """
    This component interacts with the collision map for efficient collision detection.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, parent_id, radius, offset, collision_category, collidable_categories, particle_source_name, transform_component):
        self.id = id
        # This parent_id is the id of the parent entity this collider is connected
        # to. This allows easy reference when collisions are detected for changing
        # health, experience, etc.
        self.parent_id = parent_id
        # All colliders are circular
        self.radius = radius
        # This is the offset from the center of the entity
        self.offset = offset
        # The category that this collider component falls under.
        # It can only have one as this determines which collision map to be placed in.
        self.collision_category = collision_category
        # This is a list of all of the collision categories that this collider can collide
        # with. Any colliders not under these categories will be ignored when checking collisions
        self.collidable_categories = collidable_categories
        self.particle_source_name = particle_source_name
        self.transform_component = transform_component

        self.collision_cells = set()
        # Disables collisions for instances such as a death animation or invincibility
        self.inactive = False

class HealthBar(Component):
    """
    This gives the entity a health bar, but it needs to have a 'health' property to be based
    off of. It can be offset as far from the center of the entity as needed.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, width, height, offset, transform_component):
        self.id = id
        self.width = width
        self.height = height
        self.offset = offset
        self.transform_component = transform_component
        # Creates a property that tracks the last health value so a damage bar can be made behind the health bar
        self.game.add_property(self.id, "ghost health", self.game.get_property(self.id, "health"))

class Animator(Component):
    """
    This component deals with animating entities based of the animation json files.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, animation_set, current_animations, graphics_component, transform_component):
        self.id = id
        # Could also be thought of as the animation collection
        self.animation_set = ""
        # Multiple animations can be played simultaneously if they do not inhibit each other
        # The given current animations is handled later
        self.current_animations = []
        # Properties of the animations
        self.animation_states = []
        self.graphics_component = graphics_component
        self.transform_component = transform_component
        self.current_frame = None
        # A dictionary of all of the relevant images for this animation set
        self.images = {}
        # Reset the animation data
        self.initialize_animation_set(animation_set)
        for animation in current_animations:
            # Set the properties of the animation and give it a default duration multiplier of 1
            self.add_animation_state(animation, 1)
    
    def add_animation_state(self, animation, duration_multiplier):
        """
        Sets the properties of an animation to the default values and sets the duration
        multiplier. The bigger the number, the longer the animation will play.
        """
        
        self.current_animations.append(animation)
        self.animation_states.append({
            "animation":animation,
            "duration multiplier":duration_multiplier,
            "current frame":None,
            "time accumulated":None,
            "frame time accumulated":None,
            "previous states":{},
            "played sound":False
        })
    
    def get_state_of_animation(self, animation):
        """
        Returns the animation, duration_multiplier, current_frame, start_time, and frame_start_time of an animation.
        """

        try:
            index = self.current_animations.index[animation]
            return self.animation_states[index]
        except ValueError:
            raise ValueError("Tried to get state of animation that is not in Animator!")
    
    def initialize_animation_set(self, animation_set):
        """
        Set up the animation for the first time with default data.
        """
        
        self.animation_set = animation_set
        self.images = {}
        for index, name in enumerate(self.game.animations[animation_set]["indexes"]):
            self.images.update({name:index})
        self.current_animations = []
        self.animation_states = []
    
    def play(self, animation, duration_multiplier=1):
        """
        Stops the animation if it's currently playing and then starts playing it again.
        """
        
        if animation in self.current_animations:
            self.stop(animation)
        self.add_animation_state(animation, duration_multiplier)
    
    def stop(self, animation):
        """
        Removes the given animation from the current animations.
        """
        
        try:
            index = self.current_animations.index(animation)
            self.current_animations.remove(animation)
            self.animation_states.pop(index)
        except ValueError:
            pass

class UI(Component):
    """
    This component is used to create text or buttons.
    """
    
    def __init__(self, game, next_available):
        super().__init__(game, next_available)
    
    def activate(self, id, ui_class):
        self.id = id
        self.element = ui_class
        names = {
            self.game.ui.Text:"text",
            self.game.ui.Button:"button"
        }
        # This component takes in an instance of a UI text or button object, so it gets its name based on the type
        self.name = names[type(ui_class)]
        self.checks_events = self.name in ["button"]

class System:
    """
    This is the base class for all systems. Each component type has a different system which
    holds a list of all its components. It handles creating new components, removing components,
    partitioning a buffer of components, and also has an update function which each system can override
    to update each component in whatever way is necessary.
    """
    
    def __init__(self, component_name, component_type):
        self.component_name = component_name
        # A reference to the component type so it can create
        # new instances when needed
        self.component_type = component_type
        # The list that holds all component instances. Each entity holds
        # the index reference of their component
        self.components = []
        # An index pointing to the first component that is not in use
        # When it is none, there are no more components available, so
        # the system needs to create another component buffer
        self.first_available = None
        # The highest index of a component in use
        # This tells the upate function that it doesn't need to update any
        # components past this index
        self.farthest_component = 0
    
    def add_component(self, game, *args, **kwargs):
        """
        This function partitions more instances of components if necessary,
        then activates an unused component that can be used, and returns
        the index of it for the entity to use as a reference.
        """
        
        if self.first_available is None:
            # Partitions at minimum 10 empty components, but otherwise doubles the size
            self.partition(game, max(len(self.components) + 1, 10))
        
        # Uses the first available unused component
        index = self.first_available
        # Populates the unused component with whatever data that component requires
        self.components[index].activate(*args, **kwargs)
        # Each component keeps track of what the next unused component index is past itself
        self.first_available = self.components[index].next_available
        if index > self.farthest_component:
            self.farthest_component = index
        return index
    
    def remove_component(self, index):
        try:
            # The update function uses the id to check if the component is in use or not
            # so set the id to None, but the rest of the data doesn't need to be touched
            self.components[index].id = None
            self.components[index].next_available = self.first_available
            self.first_available = index
            if index == self.farthest_component:
                while index - 1 >= 0 and self.components[index - 1].id is None:
                    index -= 1
                self.farthest_component = index
        except:
            raise Exception("Unable to remove component.")
    
    def partition(self, game, amount):
        """
        Instead of creating new instances of components on the fly when needed,
        the prevent slowdown, this function creates many instances of the components
        at once. The component has to be activated with the activate function before
        it is actually put into use.
        """
        
        # link is a reference to the next unused component
        link = None
        new_comps = []
        length = len(self.components)
        for _ in range(amount):
            component = self.component_type(game, link)
            new_comps.insert(0, component)
            # Start link at the last index and each time after, subtract one
            if link is None:
                link = length + amount - 1
            else:
                link -= 1
        # Since the partition is used if there are no longer any available components,
        # it's known that the next available component will be the first newly created component
        self.first_available = length
        self.components += new_comps
    
    def update(self):
        """
        Contains whatever code should be run for that component every loop.
        Is overridden as necessary by each component.
        """
        
        pass

class DisplayedSystem(System):
    """
    This is a subclass of the System class for use on components
    that have a visual aspect and need to display something on the screen.
    """
    
    def update(self):
        self.update_and_draw()

    def update_and_draw(self):
        pass

class TransformSystem(System):
    """
    The transform system that holds all of the transform components.
    """
    
    def __init__(self):
        super().__init__("transform", Transform)

class PhysicsSystem(System):
    """
    The physics system holds and updates all of the physics components.
    """
    
    def __init__(self):
        super().__init__("physics", Physics)
    
    def update(self, dt):
        """
        This update function handles any kind of movement for an entity be it for
        moving or rotations. It takes friction into account where applicable.
        """
        
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None: # The component is currently in use
                # Entities may want to accelerate at a different rate than they decelerate
                # This is handled by the components decel and accel values
                # The delta time is divided by 0.004 to allow the component's
                # variables to use more human usable values instead of tiny values
                if component.target_velocity == Vector2(0, 0):
                    rate_of_change = component.decel * component.friction * (dt / 0.004)
                else:
                    rate_of_change = (component.accel - component.accel * component.friction) * (dt / 0.004)
                
                if rate_of_change > 1:
                    # The rate of change is what's used to linearly interpolate from the current
                    # velocity to the desired velocity, so reaching that velocity any faster
                    # than instantaneously doesn't make sense
                    rate_of_change = 1
                component.velocity = component.velocity.lerp(component.target_velocity, rate_of_change)

                component.transform_component.pos += component.velocity * dt

                # Again, the mutliplying by 10 is so the rotational force value is more readable
                component.transform_component.rotation += component.rotational_force * 10 * dt
                # Some entities want a constant spin with no slowdown. This code is for
                # rotations with friction applied
                if component.rotation_friction and component.rotational_force:
                    # Only using this vector for its length
                    # I initialize it as a normalized vector
                    v = Vector2(1, 0) * component.rotational_force
                    v = v.lerp(Vector2(0), min(component.rotational_force * 0.05 * dt, 0.05))
                    component.rotational_force = v.length()

class GraphicsSystem(DisplayedSystem):
    """
    The graphics system holds and updates all of the graphics components. It handles
    updating image sprites of entities.
    """
    
    def __init__(self):
        super().__init__("graphics", Graphics)
        self.layer_indexes = []
        self.layers = 0
    
    def check_layer_exists(self, layer):
        """
        Instead of hardcoding the number of graphics layers that I will use, I let it create a new
        layer whenever a higher one is needed. 0 is the bottom layer (background).
        """

        while self.layers < layer + 1:
            self.layer_indexes.append([])
            self.layers += 1
    
    def add_component(self, game, *args, **kwargs):
        """
        Along with adding the new component, this function saves which layer this
        component is drawn on so it can draw each layer in the correct order.
        """
        
        layer = args[1]
        self.check_layer_exists(layer)
        index = super().add_component(game, *args, **kwargs)
        # When drawing, the graphics system will loop through the components
        # in each layer in order so the low number layers are drawn first
        self.layer_indexes[layer].append(index)
        return index
    
    def remove_component(self, index):
        """
        This function removes the component from the layer indexes before removing
        the component.
        """
        
        self.layer_indexes[self.components[index].layer].remove(index)
        super().remove_component(index)
    
    def update_and_draw(self):
        """
        This function makes any necessary changes to the images based off of animations
        or whatnot, and then blits them to the screen.
        """
        
        # Go through components in order of the layer they are in
        for layer in self.layer_indexes:
            for component_index in layer:
                component = self.components[component_index]
                # Checks both if the component is active and whether it is within view
                # It does it a cheap way by checking the center of the sprite, which
                # would cause a bigger issue the bigger the sprite
                if component.id is not None and Rect(component.game.camera.corner, (component.game.camera.width, component.game.camera.height)).collidepoint(*component.transform_component.pos):
                    # Loop through the images that make up the sprite
                    for index, image_info in enumerate(component.images_info):
                        # Check if something about the image changed and it needs to be redrawn
                        # and also check that the image is actually big enough to draw
                        if (component.was_updated(index) or component.entity_was_updated(index)) and component.get_image_property(index, "scale") != 0:
                            image, offset_vector, rotation_offset, scale_offset = image_info
                            if component.image_was_changed(index):
                                # Make both the current and previous image the same so it won't update after this
                                component.set_image_property(index, "image", image)
                                ck = image.get_colorkey()
                                width, height = image.get_size()
                                image = pygame.transform.scale(image, (max(0, math.ceil(width * scale * scale_offset)), max(0, math.ceil(height * scale * scale_offset))))
                                image = pygame.transform.rotate(image, -rotation - rotation_offset)
                                if ck:
                                    image.set_colorkey(ck)
                                component.last_used_images[index] = image
                                component.previous_images[index] = component.images[index][0]
                                component.last_edits[index] = edits.copy()
                            elif component.image_property_was_updated(index, "rotation") or component.image_property_was_updated(index, "scale"):

                            position = offset_vector + component.get_image_property(index, "position")
                            last_entity_rotation = component.last_entity_props["rotation"]
                            last_entity_scale = component.last_entity_props["scale"]
                            rotation = last_entity_rotation + component.get_image_property(index, "rotation")
                            scale = last_entity_scale * component.get_image_property(index, "scale")
                            width, height = component..get_size()
                            camera = component.game.camera
                            offset_x, offset_y = position.rotate(rotation)
                            component.game.screen.blit(component.last_used_images[index], (component.transform_component.x - width // 2 + offset_x - camera.corner.x, component.transform_component.y - height // 2 + offset_y - camera.corner.y))
                    component.last_rotation = component.transform_component.rotation

class ControllerSystem(System):
    def __init__(self):
        super().__init__("controller", Controller)

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
        super().__init__("barrel manager", BarrelManager)
    
    def update(self, frame_time):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                # update barrel animations?
                if component.shooting:
                    for barrel in component.barrels:
                        barrel[0] += frame_time
                        last_shot_accumulation, cooldown, image_index = barrel
                        image, offset_vector, rotation_offset, scale_offset = component.graphics_component.images[image_index]
                        scale = component.transform_component.scale * scale_offset
                        if last_shot_accumulation >= cooldown:
                            barrel[0] = 0
                            barrel_length = settings.BARREL_LENGTH - 10 * scale
                            barrel_angle = component.transform_component.rotation + rotation_offset
                            barrel_end = Vector2()
                            barrel_end.from_polar((barrel_length, barrel_angle))
                            offset_x, offset_y = offset_vector.rotate(component.transform_component.rotation)
                            firing_point = Vector2(component.transform_component.x + offset_x, component.transform_component.y + offset_y) + barrel_end
                            id = component.game.get_unique_id() #                         id, spawn_point, rotation, scale, angle, speed, owner
                            component.game.add_action(component.game.actions.SpawnBullet(id, component.id, firing_point, component.transform_component.rotation, scale, barrel_angle, settings.PLAYER_MAX_SPEED + 10, component.projectile_name))
                            component.animator_component.play("shoot barrel", cooldown)

class LifeTimerSystem(System):
    def __init__(self):
        super().__init__("life timer", LifeTimer)
    
    def update(self, frame_time):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                component.accumulated += frame_time
                if component.accumulated >= component.duration:
                    if component.animator_component != None:
                        if "expired" not in component.animator_component.current_animations:
                            component.animator_component.play("expired")
                            if component.game.has_component(component.id, "collider"):
                                component.game.get_component(component.id, "collider").inactive = True
                    else:
                        component.game.add_action(component.game.actions.Destroy(component.id))

class ColliderSystem(System):
    def __init__(self):
        super().__init__("collider", Collider)
    
    def add_component(self, game, *args, **kwargs):
        index = super().add_component(game, *args, **kwargs)
        self.components[index].game.get_collision_maps()[self.components[index].collision_category].insert_collider(self.components[index])
        return index
    
    def remove_component(self, index):
        try:
            self.components[index].game.get_collision_maps()[self.components[index].collision_category].remove_collider(self.components[index])
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
            if component.id is not None and not component.inactive:
                component.game.get_collision_maps()[component.collision_category].move_collider(component)
        
        # THIS IS A HORRID FUNCTION
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None and not component.inactive:
                game = component.game
                transform = component.transform_component
                origin = transform.pos + component.offset
                colliding_with_set = set().union(*[game.get_collision_maps()[c].contents.get(cell)
                        for cell in component.collision_cells for c in component.collidable_categories
                        if game.get_collision_maps()[c].contents.get(cell) != None])
                # These for loops loop through the categories that the collider is colliding with
                # and gets the cells of each, ignoring any that are empty (ie None).
                # It combines the cell sets of all the dictionaries that are in the same cell as itself.
                colliding_with_set -= {component}
                # Removes itself from the set so it doesn't collide with itself.
                for other_collider in colliding_with_set:
                    other_transform = other_collider.transform_component
                    other_origin = other_transform.pos + other_collider.offset
                    if component.parent_id != other_collider.parent_id and not other_collider.inactive and self.distance_between_squared(origin, other_origin) < (component.radius + other_collider.radius) ** 2:
                        game.helpers.handle_collision(component, other_collider) # Checks what the categories are of the colliding objects, and acts accordingly.

class HealthBarSystem(DisplayedSystem):
    def __init__(self):
        super().__init__("health bar", HealthBar)
    
    def update_and_draw(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                game = component.game
                transform = component.transform_component
                center = (transform.x + component.offset.x - game.camera.corner.x,
                    transform.y + component.offset.y - game.camera.corner.y)
                health = game.get_property(component.id, "health")
                max_health = game.get_property(component.id, "max health")
                if health < max_health:
                    ghost_health = game.get_property(component.id, "ghost health")
                    if ghost_health < health:
                        ghost_health = health
                        game.set_property(component.id, "ghost health", health)
                    else:
                        # Shrink the ghost health until it reaches the actual health
                        shrink_by = max(min(0.05, ghost_health - health), (ghost_health - health) * 0.01)
                        game.set_property(component.id, "ghost health", ghost_health - shrink_by)
                    
                    ghost_percent = ghost_health / max_health
                    width = ghost_percent * component.width
                    health_rect = Rect(0, 0, width, component.height)
                    health_rect.center = center
                    pygame.draw.rect(game.screen, game.colors.black, health_rect, 0, 2)
                    health_percent = health / max_health
                    if width - (health_percent * component.width) > 2:
                        health_rect.width -= 2
                        health_rect.height -= 2
                        health_rect.center = center
                        pygame.draw.rect(game.screen, game.colors.red, health_rect, 0, 2)
                        width = health_percent * component.width
                        health_rect = Rect(0, 0, width, component.height - 2)
                        health_rect.center = center
                        pygame.draw.rect(game.screen, game.colors.green, health_rect, 0, 2)
                    else:
                        health_rect.width -= 2
                        health_rect.height -= 2
                        health_rect.center = center
                        pygame.draw.rect(game.screen, game.colors.green, health_rect, 0, 2)
                elif game.get_property(component.id, "ghost health") != health:
                    game.set_property(component.id, "ghost health", health)

class AnimatorSystem(System):
    def __init__(self):
        super().__init__("animator", Animator)
    
    def update(self, frame_time):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None and "done with animation" not in component.current_animations:
                if Rect(component.game.camera.corner, (component.game.camera.width, component.game.camera.height)).collidepoint(*component.transform_component.pos):
                    visible = True
                else:
                    visible = False
                
                game = component.game
                anim_set = component.animation_set
                for current_animation, animation_state in zip(component.current_animations, component.animation_states):
                    if "done with animation" == current_animation:
                        break
                    animation_properties = game.animations[anim_set][current_animation]
                    duration = animation_properties["duration"] * animation_state["duration multiplier"]
                    state = animation_state
                    if state["time accumulated"] == None:
                        state["time accumulated"] = 0
                        state["frame time accumulated"] = 0
                        state["current frame"] = 0
                        state["previous states"] = {}
                        state["played sound"] = False
                        self.apply_frame(component, state, animation_properties["initial frame properties"])
                        if duration == 0:
                            self.end_animation(component, state)
                            if "done with animation" in component.current_animations:
                                break
                    elif duration > 0:
                        state["time accumulated"] += frame_time
                        state["frame time accumulated"] += frame_time
                        frame = animation_properties["frames"][state["current frame"]]
                        frame_duration = duration * frame["delay"]
                        elapsed = state["frame time accumulated"]
                        if state["time accumulated"] >= duration:
                            self.apply_frame(component, state, animation_properties["frames"][-1]["properties"])
                            self.end_animation(component, state)
                            if "done with animation" in component.current_animations:
                                break
                            continue
                        elif elapsed >= frame_duration and visible:
                            if self.go_to_next_frame(component, state, animation_properties, frame, frame_duration, elapsed):
                                frame = animation_properties["frames"][state["current frame"]]
                                frame_duration = duration * frame["delay"]
                                elapsed = state["frame time accumulated"]
                                if state["time accumulated"] >= duration:
                                    self.apply_frame(component, state, animation_properties["frames"][-1]["properties"])
                                    self.end_animation(component, state)
                                    if "done with animation" in component.current_animations:
                                        break
                                    continue
                            else:
                                continue
                        
                        if visible:
                            elapsed_percent = elapsed / frame_duration
                            self.iterate_frame(component, state, frame["properties"], elapsed_percent)
    
    def apply_frame(self, component, state, frame):
        graphics = component.graphics_component
        images = component.images
        for image, properties in frame.items():
            if image == "sound":
                name = ""
                volume = 1.0
                for property, value in properties.items():
                    if property == "name":
                        name = value
                    elif property == "volume":
                        volume = value
                
                sound = pygame.mixer.Sound(component.game.sounds[name])
                sound.set_volume(volume)
                tran = component.game.get_component(component.id, "transform")
                component.game.play_sound(sound, (tran.x, tran.y))
                state["played sound"] = True
                continue

            state["previous states"].setdefault(image, {})
            for property, value in properties.items():
                state["previous states"][image][property] = value
                graphics_image_index = images[image]
                if property == "image":
                    if value != None:
                        name = "/".join([component.animation_set, state["animation"], image])
                        graphics.switch_image_frame(graphics_image_index, component.game.animation_images[f"{name}_{value}"])
                    else:
                        graphics.switch_image_frame(graphics_image_index, None)
                elif property == "scale":
                    graphics.image_edits[graphics_image_index]["scale"] = value
                elif property == "rotation":
                    graphics.image_edits[graphics_image_index]["rotation"] = value

    def iterate_frame(self, component, state, frame, percent):
        for image, properties in frame.items():
            if image == "sound":
                if not state["played sound"]:
                    name = ""
                    volume = 1.0
                    for property, value in properties.items():
                        if property == "name":
                            name = value
                        elif property == "volume":
                            volume = value
                    
                    sound = pygame.mixer.Sound(component.game.sounds[name])
                    sound.set_volume(volume)
                    tran = component.game.get_component(component.id, "transform")
                    component.game.play_sound(sound, (tran.x, tran.y))
                    state["played sound"] = True
                
                continue
            
            previous_props = state["previous states"][image]
            for property, value in properties.items():
                graphics_image_index = component.images[image]
                try:
                    if property == "scale":
                        change = value - previous_props["scale"]
                        component.graphics_component.image_edits[graphics_image_index]["scale"] = previous_props["scale"] + change * percent
                    elif property == "rotation":
                        change = value - previous_props["rotation"]
                        component.graphics_component.image_edits[graphics_image_index]["rotation"] = previous_props["rotation"] + int(change * percent)
                except:
                    raise RuntimeError(f"'{state['animation']}' Animation missing initial {property} property.")

    def go_to_next_frame(self, component, state, animation_properties, frame, frame_duration, elapsed):
        self.apply_frame(component, state, frame["properties"])
        if state["current frame"] + 1 == len(animation_properties["frames"]):
            self.end_animation(component, state)
            return False
        else:
            past = elapsed - frame_duration
            state["current frame"] += 1
            state["frame time accumulated"] = past
            state["played sound"] = False
            return True
    
    def end_animation(self, component, state):
        props = component.game.animations[component.animation_set][state["animation"]]
        loop = props.get("loop", False)
        
        on_finish = props.get("on finish", None)
        if on_finish != None:
            if "destroy component" in on_finish:
                component.game.add_action(component.game.actions.Destroy(component.id))
            if "spawn tank particles" in on_finish:
                component.game.helpers.tank_death(component)
            if "spawn bullet particles" in on_finish:
                component.game.helpers.bullet_death(component)
            component.add_animation_state("done with animation", 1)
            return
        
        if not loop:
            component.current_animations.remove(state["animation"])
            component.animation_states.remove(state)
            component.graphics_component.reset_edits([i for i, x in enumerate(component.game.animations[component.animation_set]["indexes"]) if x != None])
        else:
            state["start time"] = None

class UISystem(DisplayedSystem):
    def __init__(self):
        super().__init__("ui", UI)
    
    def update_and_draw(self):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None:
                if component.name in ["text", "button"]:
                    if component.name == "text":
                        text = component.element
                    else:
                        text = component.element.text
                    if component.game.is_alive(text.reflect_prop[0]):
                        prop = str(component.game.get_property(*text.reflect_prop))
                        if text.text != prop:
                            text.set_text(prop)
                component.element.render(component.game.screen)
    
    def check_ui_elements_at_pos(self, event):
        for i in range(min(self.farthest_component + 1, len(self.components))):
            component = self.components[i]
            if component.id is not None and component.checks_events:
                component.element.check_event(event)

systems = [
    TransformSystem,
    PhysicsSystem,
    GraphicsSystem,
    ControllerSystem,
    BarrelManagerSystem,
    LifeTimerSystem,
    ColliderSystem,
    HealthBarSystem,
    AnimatorSystem,
    UISystem
]