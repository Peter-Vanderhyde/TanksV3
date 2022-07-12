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
        self.game = create_game_instance(self)
        self.states = states
        self.start_state = start_state
        self.state = states[start_state]
        self.last_time = time.time()
        self.frame_time = 0
    
    def start(self):
        self.state.start(self.game)
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
        current_time = time.time()
        self.frame_time = current_time - self.last_time
        self.last_time = current_time

        if self.state.switch:
            self.next_state(load_state=True)
        elif self.state.create:
            # This means you want to switch states, but you also want to restart that state
            # If you switch from the pause menu to the game, you don't want a new state
            # If you just start the game, you want a new state
            self.next_state(load_state=False)
        else:
            self.state.update(self.frame_time)
    
    def next_state(self, load_state):
        next_state = self.state.next_state
        self.state.switch = False
        self.state.create = False
        self.state.save_state()
        self.state = self.states[next_state]
        if load_state:
            self.state.load_state()
        else:
            self.state.start(self.game)
    
    def draw(self):
        self.state.draw()
        pygame.display.update()


class GameState:
    def __init__(self):
        self.switch = False
        self.create = False
        self.game = None
        self.component_systems = []
    
    def start(self, game):
        self.game = game
        self.overwrite_state()
        self.game.action_handler.set_controller_system(self.game.systems["controller"])

    def get_event(self, event):
        pass

    def update(self, frame_time):
        pass

    def draw(self):
        pass
    
    def save_state(self):
        self.component_systems = [self.game.systems, self.game.component_index, self.game.system_index]
    
    def load_state(self):
        self.game.systems, self.game.component_index, self.game.system_index = self.component_systems
    
    def overwrite_state(self):
        game = self.game
        for system in game.components.systems:
            s = system()
            game.systems[s.component_name] = s
        
        # Maps components to the index they are stored at in the entities. ie{"transform":0,"physics":1}
        for i, component in enumerate(game.systems):
            game.component_index[component] = i

        game.system_index = [system for system in game.systems.values()]



class MainMenu(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "game"
    
    def start(self, game):
        super().start(game)
        
    
    def update(self, frame_time):
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

    def update(self, frame_time):
        game = self.game
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