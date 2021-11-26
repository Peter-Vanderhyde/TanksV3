import pygame
import settings
from pygame.math import Vector2
import sys


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


class MoveLeft(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        physics = game.get_component(self.id, "physics")
        if self.move:
            physics.velx = -1
        else:
            if physics.velx == -1:
                physics.velx = 0


class MoveRight(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        physics = game.get_component(self.id, "physics")
        if self.move:
            physics.velx = 1
        else:
            if physics.velx == 1:
                physics.velx = 0


class MoveUp(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        physics = game.get_component(self.id, "physics")
        if self.move:
            physics.vely = -1
        else:
            if physics.vely == -1:
                physics.vely = 0


class MoveDown(Action):
    def __init__(self, id, move):
        super().__init__(id)
        self.move = move
    
    def execute_action(self, game):
        physics = game.get_component(self.id, "physics")
        if self.move:
            physics.vely = 1
        else:
            if physics.vely == 1:
                physics.vely = 0


class SpawnPlayer(Action):
    def __init__(self, player_id, spawn_point, rotation, scale, speed, accel, friction):
        super().__init__(player_id)
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.speed = speed
        self.accel = accel
        self.friction = friction
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.id, "graphics", [(game.images["barrel"], 0, 0), (game.images["player_body"], 0, 0)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.rotation, self.speed, self.accel, self.friction, game.get_component(self.id, "transform"))
        game.add_component(self.id, "controller", game.components.PlayerController(game, self.id, game.get_component(self.id, "transform")))
        game.add_component(self.id, "input handler", game.components.PlayerInputHandler(game, self.id, settings.PLAYER_MOVE_KEYS))


class Shoot(Action):
    def __init__(self, bullet_id, spawn_point, rotation, scale, angle, speed, projectile_type, owner_string):
        super().__init__(bullet_id)
        self.spawn_point = spawn_point
        self.rotation = rotation
        self.scale = scale
        self.angle = angle
        self.speed = speed
        self.projectile_type = projectile_type
        self.owner_string = owner_string
    
    def execute_action(self, game):
        game.create_entity(self.id)
        game.add_component(self.id, "transform", self.spawn_point.x, self.spawn_point.y, self.rotation, self.scale)
        game.add_component(self.id, "graphics", [(game.images[self.owner_string + "_" + self.projectile_type], 0, 0)], game.get_component(self.id, "transform"))
        game.add_component(self.id, "physics", self.angle, self.speed, 1, 0, game.get_component(self.id, "transform"))


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


class ActionHandler:
    def __init__(self, game, input_sys, actions=[]):
        self.game = game
        self.input_sys = input_sys
        self.actions = actions
    
    def get_player_input(self):
        events = pygame.event.get()
        for event in events:
            self.input_sys.create_player_action(event)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def handle_actions(self):
        for action in self.actions:
            action.execute(self.game)
            self.actions.pop(0)