import pygame
from pygame.locals import *
from pygame.math import Vector2
import sys
import random
import colors
import time
from ECS_test import create_game_instance


class SceneManager:
    def __init__(self, screen, start_state):
        self.screen = screen
        self.game = None
        self.states = states
        self.start_state = start_state
        self.state = states[start_state]
    
    def start(self):
        self.state.game = create_game_instance(self)
        self.state.start(self.state.game)
        self.game = self.state.game
        self.run()
    
    def run(self):
        while True:
            self.get_events()
            self.update()
            self.draw()
    
    def get_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            self.state.get_event(event)
    
    def update(self):
        if self.state.switch:
            self.next_state()
        elif self.state.create:
            # This means you want to switch states, but you also want to restart that state
            # If you switch from the pause menu to the game, you don't want a new state
            # If you just start the game, you want a new state
            self.next_state(True)
        else:
            self.state.update()
    
    def next_state(self, new=False):
        next_state = self.state.next_state
        self.state.switch = False
        self.state.create = False
        self.state = self.states[next_state]
        if new:
            self.state.game = None
            self.state.game = create_game_instance(self)
            self.state.start(self.state.game)

        self.state.game.last_time = time.time()
        self.game = self.state.game
    
    def draw(self):
        self.state.draw()
        pygame.display.update()


class GameState:
    def __init__(self):
        self.switch = False
        self.create = False
        self.game = None
    
    def start(self, game):
        self.game = game

    def get_event(self, event):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class MainMenu(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "game"
    
    def start(self, game):
        super().start(game)
        
    
    def update(self):
        pass
    
    def get_event(self, event):
        if event.type == KEYDOWN and event.key == K_RETURN:
            self.create = True
        elif event.type == KEYDOWN and event.key == K_SPACE:
            self.switch = True
    
    def draw(self):
        self.game.screen.fill(colors.white)


class Game(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "main menu"
    
    def start(self, game):
        super().start(game)
        id = game.get_unique_id()
        game.add_action(game.actions.SpawnPlayer(id, Vector2(0, 0), 0, 1, game.settings.PLAYER_MAX_SPEED, game.settings.PLAYER_ACCEL, game.settings.PLAYER_DECEL, game.settings.PLAYER_FRICTION))
        game.add_action(game.actions.FocusCamera(id, True))
        for i in range(5):
            enemy_id = game.get_unique_id()
            game.add_action(game.actions.SpawnEnemy(enemy_id, Vector2(random.randint(-1000, 1000), random.randint(-1000, 1000)), 0, 1, game.settings.PLAYER_MAX_SPEED, game.settings.PLAYER_ACCEL, game.settings.PLAYER_DECEL, game.settings.PLAYER_FRICTION))
            game.add_action(game.actions.StartFiringBarrels(enemy_id))

        game.helpers.spawn_shapes(game, 60, [Vector2(-1000, -1000), Vector2(1000, 1000)])

        game.action_handler.handle_actions()
        test = game.UI_Manager.add_button(game.ui.Text("couriernew", 20, colors.black, "Testing"),
            (300, 200), colors.black, colors.white, colors.light_gray, (100,100,100), (10, 5))
    
    def get_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_RETURN:
            self.create = True
        self.game.action_handler.get_player_input(event)

    def update(self):
        game = self.game
        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time

        game.systems["life timer"].update()
        game.systems["controller"].update()
        game.systems["barrel manager"].update()

        while game.accumulator >= game.dt:
            game.systems["physics"].update(game.dt)
            game.camera.update()
            game.systems["collider"].update()
            game.action_handler.handle_actions()
            game.accumulator -= game.dt
        
        game.systems["animator"].update()
    
    def draw(self):
        game = self.game
        game.screen.fill(colors.white)
        game.camera.draw_grid()
        game.systems["graphics"].update_and_draw()
        game.systems["health bar"].update_and_draw()
        pygame.draw.rect(game.screen, colors.black, (1, 1, game.screen.get_width(), game.screen.get_height()), 3)
        game.ui.show_fps(game.fps_text, game, game.clock)
        game.UI_Manager.render_elements()

states = {
    "main menu":MainMenu(),
    "game":Game()
}