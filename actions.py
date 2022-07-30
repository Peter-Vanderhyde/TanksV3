import pygame
import settings
from pygame.math import Vector2
import sys
import time
from ui import Anchor

'''
-----------
DEFINITIONS
-----------

Quit: ()
Move_Left: (<bool>move)
Move_Right: (<bool>move)
Move_Up: (<bool>move)
Move_Down: (<bool>move)
Spawn_Player: (player_id, spawn_point, rotation, scale, max_speed, accel, decel, friction)
Spawn_Enemy: (enemy_id, spawn_point, rotation, scale, max_speed, accel, decel, friction)
Spawn_Bullet: (bullet_id, owner_id, spawn_point, rotation, scale, angle, speed, owner_string)
Spawn_Particle: (id, image_string, spawn_point, rotation, scale, speeds: [<max_speed>, <current_speed>, <target_speed>], decel, lifetime)
Start_Firing_Barrels: (id) # Needs a barrel manager to work
Stop_Firing_Barrels: (id)
Focus_Camera: (focus_id, snap=False)
Position_Camera: (position)
Destroy: (id)
'''

class Action:
    def __init__(self, id):
        """Takes in the id that this action is applying to.
        It then checks if that id is still alive before making changes to it."""
        self.id = id

    def execute(self, game):
        self.execute_action(game)

    def execute_action(self, game):
        pass

class Quit(Action):
    def __init__(self, id=None):
        super().__init__(id)
    
    def execute_action(self, game):
        pygame.quit()
        sys.exit()

class MoveLeft(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        controller = game.get_component(self.id, "controller").controller_class
        if self.move:
            controller.velx = -1
        else:
            if controller.velx == -1:
                controller.velx = 0

class MoveRight(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        controller = game.get_component(self.id, "controller").controller_class
        if self.move:
            controller.velx = 1
        else:
            if controller.velx == 1:
                controller.velx = 0

class MoveUp(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        controller = game.get_component(self.id, "controller").controller_class
        if self.move:
            controller.vely = -1
        else:
            if controller.vely == -1:
                controller.vely = 0

class MoveDown(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        controller = game.get_component(self.id, "controller").controller_class
        if self.move:
            controller.vely = 1
        else:
            if controller.vely == 1:
                controller.vely = 0

class SpawnPlayer(Action):
    def __init__(self, player_id, spawn_point, rotation, scale, max_speed, accel, decel, friction, rotational_force=0):
        super().__init__(None)
        self.player_id = player_id
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed = max_speed
        self.current_speed = 0
        self.target_speed = 0
        self.accel = accel
        self.decel = decel
        self.friction = friction
        self.rotational_force = rotational_force
    
    def execute_action(self, game):
        game.create_entity(self.player_id)

        game.add_property(self.player_id, "health", 100)
        game.add_property(self.player_id, "max health", 100)
        game.add_property(self.player_id, "damage", 10)

        game.add_component(self.player_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        # (image, offset_vector, rotation_offset, scale_offset)
        barrels = [[game.images["barrel"], Vector2(0, 0), 0, 1]]
        game.add_component(self.player_id, "graphics", 1, barrels + [[game.images["body_player"], Vector2(0, 0), 0, 1]], game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "animator", "tank", ["spawn"], game.get_component(self.player_id, "graphics"), game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, self.accel, self.decel, self.friction, game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "controller", "player", settings.PLAYER_MOVE_KEYS, game.get_component(self.player_id, "transform"))
        # [last_shot, cooldown, image_index]
        barrels = [[0, 0.2, 0]]
        game.add_component(self.player_id, "barrel manager", barrels, False, "bullet_player", game.get_component(self.player_id, "graphics"), game.get_component(self.player_id, "transform"), game.get_component(self.player_id, "animator"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.player_id, "collider", self.player_id, 21 * game.get_component(self.player_id, "transform").scale, Vector2(0, 0), "actors", ["particles"], "body_player", game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "health bar", 50, 10, Vector2(0, -30), game.get_component(self.player_id, "transform"))

class SpawnEnemy(Action):
    def __init__(self, enemy_id, spawn_point, rotation, scale, max_speed, accel, decel, friction, rotational_force=0):
        super().__init__(None)
        self.enemy_id = enemy_id
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed = max_speed
        self.current_speed = 0
        self.target_speed = 0
        self.accel = accel
        self.decel = decel
        self.friction = friction
        self.rotational_force = rotational_force
    
    def execute_action(self, game):
        game.create_entity(self.enemy_id)

        game.add_property(self.enemy_id, "health", 100)
        game.add_property(self.enemy_id, "max health", 100)
        game.add_property(self.enemy_id, "damage", 10)

        game.add_component(self.enemy_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        # (image, offset_vector, rotation_offset, scale_offset)
        barrels = [[game.images["barrel"], Vector2(0, 0), 0, 1]]
        game.add_component(self.enemy_id, "graphics", 1, barrels + [[game.images["body_enemy"], Vector2(0, 0), 0, 1]], game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "animator", "tank", ["spawn"], game.get_component(self.enemy_id, "graphics"), game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, self.accel, self.decel, self.friction, game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "controller", "enemy", game.get_component(self.enemy_id, "transform"))
        # [scale, angle_offset, last_shot, cooldown, image_index]
        barrels = [[0, 0.2, 0]]
        game.add_component(self.enemy_id, "barrel manager", barrels, False, "bullet_enemy", game.get_component(self.enemy_id, "graphics"), game.get_component(self.enemy_id, "transform"), game.get_component(self.enemy_id, "animator"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.enemy_id, "collider", self.enemy_id, 21 * game.get_component(self.enemy_id, "transform").scale, Vector2(0, 0), "actors", ["particles"], "body_enemy", game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "health bar", 50, 10, Vector2(0, -30), game.get_component(self.enemy_id, "transform"))

class SpawnBullet(Action):
    def __init__(self, bullet_id, owner_id, spawn_point, rotation, scale, angle, speed, projectile_name, rotational_force=0):
        super().__init__(None)
        self.bullet_id = bullet_id
        self.owner_id = owner_id
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.angle = angle
        self.speed = speed
        self.projectile_name = projectile_name
        self.rotational_force = rotational_force
    
    def execute_action(self, game):
        if not game.is_alive(self.owner_id):
            return
        game.create_entity(self.bullet_id)
        game.add_component(self.bullet_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.bullet_id, "graphics", 0, [(game.images[self.projectile_name], Vector2(0, 0), 0, 1)], game.get_component(self.bullet_id, "transform"))
        game.add_component(self.bullet_id, "physics", self.angle, (self.speed, self.speed, self.speed), self.rotational_force, 1, 1, 0, game.get_component(self.bullet_id, "transform"))
        game.add_component(self.bullet_id, "animator", "bullet", [], game.get_component(self.bullet_id, "graphics"), game.get_component(self.bullet_id, "transform"))
        game.add_component(self.bullet_id, "life timer", time.time(), 3, game.get_component(self.bullet_id, "animator"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.bullet_id, "collider", self.owner_id, 10, Vector2(0, 0), "projectiles", ["actors", "projectiles", "shapes"], self.projectile_name, game.get_component(self.bullet_id, "transform"))
        game.add_property(self.bullet_id, "damage", game.get_property(self.owner_id, "damage"))

class SpawnShape(Action):
    def __init__(self, shape_id, spawn_point, rotation, scale, xp, spin_rate=0, spin_friction=True):
        super().__init__(None)
        self.shape_id = shape_id
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.xp = xp
        self.spin_rate = spin_rate
        self.spin_friction = spin_friction
    
    def execute_action(self, game):
        game.create_entity(self.shape_id)
        game.add_component(self.shape_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.shape_id, "graphics", 0, [(game.images["square_small"], Vector2(0, 0), 0, 1)], game.get_component(self.shape_id, "transform"))
        game.add_component(self.shape_id, "physics", self.rotation, (0, 0, 0), self.spin_rate, 1, 0.7, settings.PARTICLE_FRICTION, game.get_component(self.shape_id, "transform"), self.spin_friction)
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.shape_id, "collider", self.shape_id, 8, Vector2(0, 0), "shapes", [], "", game.get_component(self.shape_id, "transform"))
        game.add_property(self.shape_id, "xp", self.xp)
        game.add_property(self.shape_id, "health", 30)

class SpawnParticle(Action):
    def __init__(self, particle_id, image_string, spawn_point, rotation, scale, speeds, decel, lifetime, rotational_force=0, rotation_friction=True, friction=settings.PARTICLE_FRICTION, collide=False):
        super().__init__(None)
        self.particle_id = particle_id
        self.image_string = image_string
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed, self.current_speed, self.target_speed = speeds
        self.decel = decel
        self.lifetime = lifetime
        self.rotational_force = rotational_force
        self.rotation_friction = rotation_friction
        self.friction = friction
        self.collide = collide
    
    def execute_action(self, game):
        game.create_entity(self.particle_id)
        game.add_component(self.particle_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.particle_id, "graphics", 0, [(game.images[self.image_string], Vector2(0, 0), 0, 1)], game.get_component(self.particle_id, "transform"))
        game.add_component(self.particle_id, "animator", "particle", [], game.get_component(self.particle_id, "graphics"), game.get_component(self.particle_id, "transform"))
        game.add_component(self.particle_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, 1, self.decel, self.friction, game.get_component(self.particle_id, "transform"), rotation_friction=self.rotation_friction)
        game.add_component(self.particle_id, "life timer", time.time(), self.lifetime, game.get_component(self.particle_id, "animator"))
        if self.collide:
            if "particle_enemy" in self.image_string or "particle_player" in self.image_string:
                radius = 7 * self.scale
            elif "particle_2" in self.image_string:
                radius = 6 * self.scale
            elif "particle_3" in self.image_string:
                radius = 3 * self.scale
            game.add_component(self.particle_id, "collider", self.particle_id, radius, Vector2(0, 0), "particles", [], "", game.get_component(self.particle_id, "transform"))

class StartFiringBarrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        if not game.is_alive(self.id):
            return
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = True

class StopFiringBarrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        if not game.is_alive(self.id):
            return
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = False

class FocusCamera(Action):
    def __init__(self, focus_id, snap=False):
        super().__init__(focus_id)
        self.snap = snap
    
    def execute_action(self, game):
        if game.is_alive(self.id):
            game.camera.set_target(self.id, self.snap)
        else:
            game.camera.clear_target()

class PositionCamera(Action):
    def __init__(self, position):
        super().__init__(None)
        self.position = position
    
    def execute_action(self, game):
        game.camera.set_position(self.position)

class Destroy(Action):
    def __init__(self, id, change_focus=None):
        super().__init__(id)
        self.change_focus = change_focus
    
    def execute_action(self, game):
        if not game.is_alive(self.id):
            return
        game.destroy_entity(self.id)
        if self.change_focus != None:
            game.add_action(game.actions.FocusCamera(self.change_focus))
        elif game.camera.target_id == self.id:
            game.camera.clear_target()

class Damage(Action):
    def __init__(self, id_to_damage, damage):
        super().__init__(id_to_damage)
        self.damage = damage
    
    def execute_action(self, game):
        if not game.is_alive(self.id):
            return
        health = game.get_property(self.id, "health")
        game.set_property(self.id, "health", health - self.damage)

class CreateText(Action):
    def __init__(self, text_id, font_name, size, color, reflect_prop=(), anchor=Anchor("top left", (0, 0))):
        super().__init__(None)
        self.text_id = text_id
        self.font_name = font_name
        self.size = size
        self.color = color
        self.get_id = reflect_prop[0]
        self.get_prop = reflect_prop[1]
        if self.get_id == self.text_id:
            self.text = reflect_prop[2]
        # This will be what entity it will get the text from, and what property to use.
        # e.g. (id, prop) -> (46, "health")
        # (self.id, "title", "Click Me")
        # When just getting text that will not change, use the component's id as the first argument, pick a prop name,
        # and put the text as the last arg.
        self.anchor = anchor
    
    def execute_action(self, game):
        game.create_entity(self.text_id)
        if self.get_id == self.text_id:
            game.add_property(self.get_id, self.get_prop, self.text)
        
        game.add_component(self.text_id, "ui", game.ui.Text(self.font_name, self.size, self.color, (self.get_id, self.get_prop), self.anchor))


class ActionHandler:
    def __init__(self, game, actions=[]):
        self.game = game
        self.controller_sys = None
        self.actions = actions
    
    def set_controller_system(self, controller_sys):
        self.controller_sys = controller_sys
    
    def get_player_input(self, event):
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            self.game.ui_manager.check_ui_elements_at_pos(event)
        self.controller_sys.get_action_from_event(event)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def handle_actions(self):
        for action in self.actions:
            if action.id == None or self.game.is_alive(action.id):
                action.execute(self.game)
        self.actions = []