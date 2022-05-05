import pygame
import settings
from pygame.math import Vector2
import sys
import time

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
        """Takes in the id that this action is applying to"""
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
        barrels = [(game.images["barrel"], Vector2(0, 0), 0, 1)]
        game.add_component(self.player_id, "graphics", 1, barrels + [(game.images["body_player"], Vector2(0, 0), 0, 1)], game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, self.accel, self.decel, self.friction, game.get_component(self.player_id, "transform"))
        game.add_component(self.player_id, "controller", game.components.PlayerController(game, self.player_id, settings.PLAYER_MOVE_KEYS, game.get_component(self.player_id, "transform")))
        # [last_shot, cooldown, image_index]
        barrels = [[0, 0.2, 0]]
        game.add_component(self.player_id, "barrel manager", barrels, False, "bullet_player", game.get_component(self.player_id, "graphics"), game.get_component(self.player_id, "transform"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.player_id, "collider", self.player_id, 21, Vector2(0, 0), "actors", [], "body_player", game.get_component(self.player_id, "transform"))
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
        barrels = [(game.images["barrel"], Vector2(0, 0), 0, 1)]
        game.add_component(self.enemy_id, "graphics", 1, barrels + [(game.images["body_enemy"], Vector2(0, 0), 0, 1)], game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, self.accel, self.decel, self.friction, game.get_component(self.enemy_id, "transform"))
        game.add_component(self.enemy_id, "controller", game.components.EnemyController(game, self.enemy_id, game.get_component(self.enemy_id, "transform")))
        # [scale, angle_offset, last_shot, cooldown, image_index]
        barrels = [[0, 0.2, 0]]
        game.add_component(self.enemy_id, "barrel manager", barrels, False, "bullet_enemy", game.get_component(self.enemy_id, "graphics"), game.get_component(self.enemy_id, "transform"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.enemy_id, "collider", self.enemy_id, 21, Vector2(0, 0), "actors", [], "body_enemy", game.get_component(self.enemy_id, "transform"))
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
        game.create_entity(self.bullet_id)
        game.add_component(self.bullet_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.bullet_id, "graphics", 0, [(game.images[self.projectile_name], Vector2(0, 0), 0, 1)], game.get_component(self.bullet_id, "transform"))
        game.add_component(self.bullet_id, "physics", self.angle, (self.speed, self.speed, self.speed), self.rotational_force, 1, 1, 0, game.get_component(self.bullet_id, "transform"))
        game.add_component(self.bullet_id, "life timer", time.time(), 3)
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
        game.add_component(self.shape_id, "collider", self.shape_id, 8, Vector2(0, 0), "shapes", ["projectiles"], "", game.get_component(self.shape_id, "transform"))
        game.add_property(self.shape_id, "xp", self.xp)
        game.add_property(self.shape_id, "health", 30)

class SpawnParticle(Action):
    def __init__(self, particle_id, image_string, spawn_point, rotation, scale, speeds, decel, lifetime, rotational_force=0, rotation_friction=True, friction=settings.PARTICLE_FRICTION):
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
    
    def execute_action(self, game):
        game.create_entity(self.particle_id)
        game.add_component(self.particle_id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.particle_id, "graphics", 0, [(game.images[self.image_string], Vector2(0, 0), 0, 1)], game.get_component(self.particle_id, "transform"))
        game.add_component(self.particle_id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.rotational_force, 1, self.decel, self.friction, game.get_component(self.particle_id, "transform"), rotation_friction=self.rotation_friction)
        game.add_component(self.particle_id, "life timer", time.time(), self.lifetime)

class StartFiringBarrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = True

class StopFiringBarrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = False

class FocusCamera(Action):
    def __init__(self, focus_id, snap=False):
        super().__init__(focus_id)
        self.snap = snap
    
    def execute_action(self, game):
        game.camera.set_target(self.id, self.snap)

class PositionCamera(Action):
    def __init__(self, position):
        super().__init__(None)
        self.position = position
    
    def execute_action(self, game):
        game.camera.set_position(self.position)

class Destroy(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        game.destroy_entity(self.id)
        if game.camera.target_id == self.id:
            game.camera.clear_target()

class Damage(Action):
    def __init__(self, id_to_damage, damage):
        super().__init__(id_to_damage)
        self.damage = damage
    
    def execute_action(self, game):
        health = game.get_property(self.id, "health")
        game.set_property(self.id, "health", health - self.damage)



class ActionHandler:
    def __init__(self, game, controller_sys, actions=[]):
        self.game = game
        self.controller_sys = controller_sys
        self.actions = actions
    
    def get_player_input(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            else:
                self.controller_sys.get_action_from_event(event)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def handle_actions(self):
        for action in self.actions:
            if action.id == None or self.game.is_alive(action.id):
                action.execute(self.game)
        self.actions = []