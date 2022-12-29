import pygame
from pygame.locals import *
from pygame.math import Vector2
import math

class EnemyController:
    """
    This class is in charge of enemy behavior. It is responsible for
    shooting, aiming, and eventually movement.
    """
    
    def __init__(self, game, id, transform_component):
        self.game = game
        self.id = id
        self.transform_component = transform_component
    
    def update(self):
        transform = self.transform_component
        player = self.game.get_player()
        if player: # Player is alive
            p_trans = self.game.get_component(player, "transform")
            target = Vector2(p_trans.x, p_trans.y)
            origin = Vector2(transform.x, transform.y)
            target_angle = self.game.helpers.angle_toward(origin, target)
            current_angle = transform.rotation
            # Used to fix angle discrepencies when going from 0 to 360 degrees
            current_angle, target_angle = self.game.helpers.fix_angle_difference(current_angle, target_angle)
            # Slowly rotate toward player
            new_angle = Vector2(current_angle, 0).lerp(Vector2(target_angle, 0), 0.005 * (self.game.dt / 0.004)).x
            transform.rotation = new_angle

    def get_action(self, event):
        pass

class PlayerController:
    """
    Handles player input.
    """
    
    def __init__(self, game, id, move_keys, transform_component, physics_component):
        self.game = game
        self.id = id
        self.move_keys = move_keys
        self.transform_component = transform_component
        self.physics_component = physics_component
        self.velx = 0
        self.vely = 0
    
    def update(self):
        # Point player towards mouse
        transform = self.transform_component
        physics = self.physics_component
        distance_between = (pygame.mouse.get_pos() + self.game.camera.corner) - Vector2(transform.x, transform.y)
        angle = distance_between.as_polar()[1]
        transform.rotation = angle

        # Setting the target velocity to key presses
        physics.target_velocity = Vector2(self.velx, self.vely)
        if (self.velx, self.vely) != (0, 0):
            # A key is being pressed
            physics.target_velocity.scale_to_length(physics.max_speed)
    
    def get_action(self, event):
        action = self.game.actions
        if event.type == KEYDOWN:
            if event.key == self.move_keys["left"]:
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
                return action.StartFiringBarrels(self.id)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                return action.StopFiringBarrels(self.id)

name_dict = {
    'player': PlayerController,
    'enemy': EnemyController
}