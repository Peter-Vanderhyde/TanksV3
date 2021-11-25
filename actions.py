import pygame
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
    def __init__(self, id, max_vel, accel):
        super().__init__(id)
        self.max_vel = max_vel
        self.accel = accel
    
    def execute_action(self, game):
        physics = game.get_component(self.id, "physics")
        physics.velocity = physics.velocity.lerp(self.max_vel, self.accel)


class ActionHandler:
    def __init__(self, game, input_sys, actions=[]):
        self.game = game
        self.input_sys = input_sys
        self.actions = actions
    
    def get_player_input(self):
        events = pygame.event.get()
        for event in events:
            self.input_sys.create_player_action(event, self)
    
    def add_action(self, action):
        self.actions.append(action)
    
    def handle_actions(self):
        for action in self.actions:
            action.execute(self.game)
            self.actions.pop(0)