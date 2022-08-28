import pygame
from pygame.locals import *
from pygame.math import Vector2
import sys
import random
import colors
import time
from ECS_test import Camera, create_game_instance
from ui import Anchor

class StateContainer:
    def __init__(self, game):
        self.time_of_save = time.time()
        self.systems = {}
        self.component_index = {}
        self.system_index = []

        self.entities = {}
        self.entity_props = {}
        self.living_entities = 0
        self.last_id = 0

        self.collision_maps = {}

        self.actions = []
        self.camera = None
        self.player = None

        for system in game.components.systems:
            s = system()
            self.systems[s.component_name] = s
        
        # Maps components to the index they are stored at in the entities. ie{"transform":0,"physics":1}
        for i, component in enumerate(self.systems):
            self.component_index[component] = i

        self.system_index = [system for system in self.systems.values()]

        for category in game.settings.COLLISION_CATEGORIES:
            self.collision_maps[category] = game.grid_manager(game.collision_grid_width)
        
        # Not in use. Perhaps for future use when attacking on sight
        self.collision_maps["in view"] = game.grid_manager(game.screen.get_width(), game.screen.get_height())
        
        game.action_handler.set_controller_system(self.systems["controller"])

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
        self.game.dt = self.frame_time

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
        self.state_container = None
    
    def start(self, game):
        self.game = game
        self.overwrite_state()

    def get_event(self, event):
        pass

    def update(self, frame_time):
        pass

    def draw(self):
        pass
    
    def save_state(self):
        self.game.state_container.actions = self.game.action_handler.actions
        self.game.action_handler.actions = []
        self.game.state_container.camera = self.game.camera
        self.state_container = self.game.state_container
        self.state_container.time_of_save = time.time()
    
    def load_state(self):
        self.game.state_container = self.state_container
        self.game.action_handler.set_controller_system(self.game.get_systems()["controller"])
        self.game.action_handler.actions = self.game.state_container.actions
        self.game.camera = self.game.state_container.camera
        self.game.resync_components()
    
    def overwrite_state(self):
        self.game.state_container = StateContainer(self.game)
        self.game.camera = Camera(self.game)


class MainMenu(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "game"
    
    def start(self, game):
        super().start(game)
        # Creates title text
        title = game.get_unique_id()
        game.add_action(game.actions.CreateText(title, "segoeprint", 50, colors.black, (title, "title", "Work In Progress"),
            Anchor("center", (game.screen.get_width() // 2 - 4, game.screen.get_height() // 4 + 4))))
        game.add_action(game.actions.CreateText(game.get_unique_id(), "segoeprint", 50, colors.blue, (title, "title"),
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 4))))
        
        # Creates start button
        play_button = game.get_unique_id()
        t = game.ui.Text("couriernew", 20, (0, 0, 150), (play_button, "text", "Play"))
        def func(g, x):
            g.scene_manager.state.create = x
        game.add_action(game.actions.CreateButton(play_button, t,
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 2)), colors.black, colors.white,
            colors.light_gray, colors.green, (func, (game, True)), padding=(20, 10), outline_width=3))
        
        # Creates exit button
        exit_button = game.get_unique_id()
        t = game.ui.Text("couriernew", 20, (0, 0, 150), (exit_button, "text", "Exit"))
        game.add_action(game.actions.CreateButton(exit_button, t,
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 2 + 100)), colors.black, colors.white,
            colors.light_gray, colors.green, (game.add_action, game.actions.Quit()), padding=(20, 10), outline_width=3))
        
        # for i in range(5):
        #     enemy_id = game.get_unique_id()
        #     size = game.screen.get_size()
        #     game.add_action(game.actions.SpawnEnemy(enemy_id, Vector2(random.randint(0, size[0]), random.randint(0, size[1])), 0, 1, game.settings.PLAYER_MAX_SPEED, game.settings.PLAYER_ACCEL, game.settings.PLAYER_DECEL, game.settings.PLAYER_FRICTION))
        #     game.add_action(game.actions.StartFiringBarrels(enemy_id))
        
        game.add_action(game.actions.PositionCamera(Vector2((game.screen.get_width() // 2, game.screen.get_height() // 2))))
    
    def update(self, frame_time):
        game = self.game
        game.accumulator += frame_time

        game.get_systems()["life timer"].update(frame_time)
        game.get_systems()["controller"].update()
        game.get_systems()["barrel manager"].update(frame_time)

        while game.accumulator >= frame_time:
            game.get_systems()["physics"].update(frame_time)
            game.camera.update()
            game.get_systems()["collider"].update()
            game.action_handler.handle_actions()
            game.accumulator -= frame_time
        
        game.get_systems()["animator"].update(frame_time)
        game.play_sounds()
    
    def get_event(self, event):
        if event.type == KEYDOWN and event.key == K_RETURN:
            self.create = True
        elif event.type == KEYDOWN and event.key == K_SPACE:
            self.switch = True
        self.game.action_handler.get_player_input(event)
    
    def draw(self):
        self.game.screen.fill(colors.white)
        self.game.get_systems()["graphics"].update_and_draw()
        self.game.get_systems()["health bar"].update_and_draw()
        self.game.get_systems()["ui"].update_and_draw()

class PauseMenu(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "main menu"
        self.background = pygame.Surface
    
    def start(self, game):
        super().start(game)
        self.background = pygame.display.get_surface().copy()
        temp = pygame.Surface((self.background.get_width(), self.background.get_height())).convert_alpha()
        temp.fill((0, 0, 0, 50))
        self.background.blit(temp, (0, 0))
        title = game.get_unique_id()
        game.add_action(game.actions.CreateText(title, "segoeprint", 40, colors.black, (title, "title", "Pause Menu"),
            Anchor("center", (game.screen.get_width() // 2 - 4, game.screen.get_height() // 4 + 4))))
        game.add_action(game.actions.CreateText(game.get_unique_id(), "segoeprint", 40, colors.blue, (title, "title"),
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 4))))
        
        # Creates continue button
        continue_button = game.get_unique_id()
        t = game.ui.Text("couriernew", 30, (0, 0, 150), (continue_button, "text", "Continue"))
        def func(g, x):
            g.scene_manager.state.next_state = "game"
            g.scene_manager.state.switch = x
        game.add_action(game.actions.CreateButton(continue_button, t,
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 2)), colors.black, colors.white,
            colors.light_gray, colors.green, (func, (game, True)), padding=(20, 10), outline_width=3))
        
        # Creates exit button
        exit_menu_button = game.get_unique_id()
        t = game.ui.Text("couriernew", 30, (0, 0, 150), (exit_menu_button, "text", "Exit to Menu"))
        def func(g, x):
            g.scene_manager.state.next_state = "main menu"
            g.scene_manager.state.create = x
        game.add_action(game.actions.CreateButton(exit_menu_button, t,
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 2 + 100)), colors.black, colors.white,
            colors.light_gray, colors.green, (func, (game, True)), padding=(20, 10), outline_width=3))

        exit_game_button = game.get_unique_id()
        t = game.ui.Text("couriernew", 30, (0, 0, 150), (exit_game_button, "text", "Exit Game"))
        game.add_action(game.actions.CreateButton(exit_game_button, t,
            Anchor("center", (game.screen.get_width() // 2, game.screen.get_height() // 2 + 200)), colors.black, colors.white,
            colors.light_gray, colors.green, (game.add_action, game.actions.Quit()), padding=(20, 10), outline_width=3))
    
    def update(self, frame_time):
        self.game.action_handler.handle_actions()
    
    def get_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.next_state = "game"
            self.switch = True
        self.game.action_handler.get_player_input(event)
    
    def draw(self):
        #self.game.screen.fill(colors.white)
        self.game.screen.blit(self.background, (0, 0))
        self.game.get_systems()["ui"].update_and_draw()

class Game(GameState):
    def __init__(self):
        super().__init__()
        self.next_state = "pause menu"
        self.fps_text = None
    
    def start(self, game):
        super().start(game)
        def temp_func():
            player_id = game.get_unique_id()
            game.add_action(game.actions.SpawnPlayer(player_id, Vector2(0, 0), 0, 1, game.settings.PLAYER_MAX_SPEED, game.settings.PLAYER_ACCEL, game.settings.PLAYER_DECEL, game.settings.PLAYER_FRICTION))
            game.add_action(game.actions.FocusCamera(player_id, True))
        
        effect_id = game.get_unique_id()
        game.add_action(game.actions.SpawnEffect(effect_id, "player vortex", (0, 0), trigger_on_death=temp_func))
        game.add_action(game.actions.FocusCamera(effect_id, True))

        def temp_func(position):
            enemy_id = game.get_unique_id()
            game.add_action(game.actions.SpawnEnemy(enemy_id, position, 0, 1, game.settings.PLAYER_MAX_SPEED, game.settings.PLAYER_ACCEL, game.settings.PLAYER_DECEL, game.settings.PLAYER_FRICTION))
            game.add_action(game.actions.StartFiringBarrels(enemy_id))
        
        for i in range(5):
            position = Vector2(random.randint(-1000, 1000), random.randint(-1000, 1000))
            effect_id = game.get_unique_id()
            game.add_action(game.actions.SpawnEffect(effect_id, "enemy vortex", position, trigger_on_death=temp_func, args=position))

        game.helpers.spawn_shapes(game, 60, [Vector2(-1000, -1000), Vector2(1000, 1000)])

        game.action_handler.handle_actions()

        self.fps_text = game.get_unique_id()
        game.add_action(game.actions.CreateText(self.fps_text, "couriernew", 15, colors.blue, (self.fps_text, "fps info", "temp"),
            Anchor("top left", (6, 0))))

        #test = game.get_unique_id()
        #text = game.ui.Text("couriernew", 20, colors.black, (test, "text", "Testing"))
        #game.add_action(game.actions.CreateButton(test, text, Anchor("center", (300, 200)), colors.black,
        #    colors.white, colors.light_gray, (100, 100, 100), (10, 5)))
    
    def get_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.next_state = "pause menu"
            self.create = True
        
        self.game.action_handler.get_player_input(event)

    def update(self, frame_time):
        #frame_time /= 2
        game = self.game
        game.accumulator += frame_time

        game.get_systems()["life timer"].update(frame_time)
        game.get_systems()["controller"].update()
        game.get_systems()["barrel manager"].update(frame_time)

        while game.accumulator >= frame_time:
            game.get_systems()["physics"].update(frame_time)
            game.camera.update()
            game.get_systems()["collider"].update()
            game.action_handler.handle_actions()
            game.accumulator -= frame_time
        
        game.get_systems()["animator"].update(frame_time)
        #game.play_sounds()
        game.sounds_to_play = []
    
    def draw(self):
        game = self.game
        game.screen.fill(colors.white)
        game.camera.draw_grid()
        game.get_systems()["graphics"].update_and_draw()
        game.get_systems()["health bar"].update_and_draw()
        pygame.draw.rect(game.screen, colors.black, (1, 1, game.screen.get_width(), game.screen.get_height()), 3)
        game.ui.update_fps_info(self.fps_text, game, game.clock)
        game.get_systems()["ui"].update_and_draw()

states = {
    "main menu":MainMenu(),
    "game":Game(),
    "pause menu":PauseMenu()
}