import pygame
import sys


class Action:
    def __init__(self, id):
        self.id = id

    def execute(self):
        self.execute_action()

    def execute_action(self):
        pass


class Quit(Action):
    def __init__(self, id=None):
        super().__init__(id)
    
    def execute_action(self):
        pygame.quit()
        sys.exit()


class ActionHandler:
    def __init__(self, input_sys, actions=[]):
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
            action.execute()
            self.actions.pop(0)