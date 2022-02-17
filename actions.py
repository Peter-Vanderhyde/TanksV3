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

class Move_Left(Action):
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

class Move_Right(Action):
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

class Move_Up(Action):
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

class Move_Down(Action):
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

class Spawn_Player(Action):
    def __init__(self, player_id, spawn_point, rotation, scale, max_speed, accel, decel, friction):
        super().__init__(player_id)
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed = max_speed
        self.current_speed = 0
        self.target_speed = 0
        self.accel = accel
        self.decel = decel
        self.friction = friction
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        # (image, offset_vector, rotation_offset, scale_offset)
        barrels = [(game.images["barrel"], Vector2(0, 0), 0, 1)]
        game.add_component(self.id, "graphics", 1, barrels + [(game.images["player_body"], Vector2(0, 0), 0, 1)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.accel, self.decel, self.friction, game.get_component(self.id, "transform"))
        game.add_component(self.id, "controller", game.components.Player_Controller(game, self.id, settings.PLAYER_MOVE_KEYS, game.get_component(self.id, "transform")))
        # [last_shot, cooldown, image_index]
        barrels = [[0, 0.5, 0]]
        game.add_component(self.id, "barrel manager", barrels, False, "player", game.get_component(self.id, "graphics"), game.get_component(self.id, "transform"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.id, "collider", self.id, 21, Vector2(0, 0), "actors", [], game.get_component(self.id, "transform"))

class Spawn_Enemy(Action):
    def __init__(self, enemy_id, spawn_point, rotation, scale, max_speed, accel, decel, friction):
        super().__init__(enemy_id)
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed = max_speed
        self.current_speed = 0
        self.target_speed = 0
        self.accel = accel
        self.decel = decel
        self.friction = friction
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        # (image, offset_vector, rotation_offset, scale_offset)
        barrels = [(game.images["barrel"], Vector2(0, 0), 0, 1)]
        game.add_component(self.id, "graphics", 1, barrels + [(game.images["enemy_body"], Vector2(0, 0), 0, 1)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), self.accel, self.decel, self.friction, game.get_component(self.id, "transform"))
        game.add_component(self.id, "controller", game.components.Enemy_Controller(game, self.id, game.get_component(self.id, "transform")))
        # [scale, angle_offset, last_shot, cooldown, image_index]
        barrels = [[0, 0.5, 0]]
        game.add_component(self.id, "barrel manager", barrels, False, "enemy", game.get_component(self.id, "graphics"), game.get_component(self.id, "transform"))
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.id, "collider", self.id, 21, Vector2(0, 0), "actors", [], game.get_component(self.id, "transform"))

class Spawn_Bullet(Action):
    def __init__(self, bullet_id, owner_id, spawn_point, rotation, scale, angle, speed, owner_string):
        super().__init__(bullet_id)
        self.owner_id = owner_id
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.angle = angle
        self.speed = speed
        self.owner_string = owner_string
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.id, "graphics", 0, [(game.images[self.owner_string + "_bullet"], Vector2(0, 0), 0, 1)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.angle, (self.speed, self.speed, self.speed), 1, 1, 0, game.get_component(self.id, "transform"))
        game.add_component(self.id, "life timer", time.time(), 3)
        # Collider: [collision_check_id, radius, offset, collision_category, collidable_width, transform_component]
        game.add_component(self.id, "collider", self.owner_id, 10, Vector2(0, 0), "projectiles", ["actors", "projectiles"], game.get_component(self.id, "transform"))

class Spawn_Particle(Action):
    def __init__(self, id, image_string, spawn_point, rotation, scale, speeds, decel, lifetime):
        super().__init__(id)
        self.image_string = image_string
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.max_speed, self.current_speed, self.target_speed = speeds
        self.decel = decel
        self.lifetime = lifetime
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.id, "graphics", 0, [(game.images[self.image_string], Vector2(0, 0), 0, 1)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.rotation, (self.max_speed, self.current_speed, self.target_speed), 1, self.decel, settings.PLAYER_FRICTION, game.get_component(self.id, "transform"))
        game.add_component(self.id, "life timer", time.time(), self.lifetime)

class Start_Firing_Barrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = True

class Stop_Firing_Barrels(Action):
    def __init__(self, id):
        super().__init__(id)
    
    def execute_action(self, game):
        manager = game.get_component(self.id, "barrel manager")
        manager.shooting = False

class Focus_Camera(Action):
    def __init__(self, focus_id, snap=False):
        super().__init__(focus_id)
        self.snap = snap
    
    def execute_action(self, game):
        game.camera.set_target(self.id, self.snap)

class Position_Camera(Action):
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

class Action_Handler:
    def __init__(self, game, controller_sys, actions=[]):
        self.game = game
        self.controller_sys = controller_sys
        self.actions = actions
    
    def get_player_input(self):
        events = pygame.event.get()
        for event in events:
            self.controller_sys.get_action_from_event(event)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def handle_actions(self):
        for action in self.actions:
            action.execute(self.game)
        self.actions = []