import pygame
import time
import components
import actions
import colors
import settings
import spatial_hashing
from pygame.locals import *
from pygame.math import Vector2
pygame.init()


def load_image(name, alpha=True, colorkey=()):
    if alpha:
        image = pygame.image.load(settings.IMAGE_PATH + name + ".png").convert_alpha()
        if colorkey != ():
            image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(settings.IMAGE_PATH + name + ".png").convert()
    return image


def load_images():
    d = {}
    for asset in settings.ASSETS:
        image = load_image(*asset)
        d.update({asset[0]:image})
    
    return d


class Game:
    def __init__(self, screen, collision_grid_width):
        self.screen = screen
        self.collision_grid_width = collision_grid_width
        self.components = components
        self.actions = actions
        self.images = {}

        self.dt = 0.01
        self.last_time = time.time()
        self.accumulator = 0.0

        self.entities = {}
        self.living_entities = 0
        self.last_id = 0

        #TODO Fix this action controller system at some point
        self.action_handler = actions.Action_Handler(self, components.controller_sys)
        self.camera = Camera(self)

        self.entity_props = {}

        #self.collision_tree = q_tree.Quad_Tree(Vector2(-1000000, -1000000), Vector2(1000000, 1000000))
        GM = spatial_hashing.Grid_Manager
        collision_categories = ["projectiles", "actors", "objects"]
        self.collision_maps = {}
        for category in collision_categories:
            self.collision_maps[category] = GM(self.collision_grid_width)
    
    def get_unique_id(self):
        """Keeps track of the last given id so it's guaranteed to be unique"""
        self.last_id += 1
        return self.last_id - 1
    
    def create_entity(self, entity_id):
        """Adds a new id to the entity dictionary with each component index
        defaulted to -1 since it's not yet known what components it will have"""
        # Create [-1, -1, -1, etc] because we don't know what components it will have
        component_indexes = [-1] * len(components.system_index)
        # Each entity is just this list of component indexes associated with an id key
        self.entities[entity_id] = component_indexes
        self.living_entities += 1
        self.entity_props[entity_id] = {}

    def add_component(self, entity_id, component_name, *args, **kwargs):
        """Give the given entity a new component such as physics or graphics"""
        index = components.systems[component_name].add_component(self, entity_id, *args, **kwargs)
        self.entities[entity_id][components.component_index[component_name]] = index
        return entity_id
    
    def add_property(self, entity_id, property, value):
        """Add a new property to this entity (i.e. health)"""
        self.set_property(entity_id, property, value)
    
    def destroy_entity(self, entity_id):
        """Deactivates each of the components of the given entity"""
        try:
            for i, index in enumerate(self.entities[entity_id]):
                if index != -1:
                    components.system_index[i].remove_component(index)
            self.entities.pop(entity_id)
            self.living_entities -= 1
        except:
            pass

    def get_component(self, entity_id, component_name):
        """Returns the given component of the given entity"""
        try:
            component = self.components.systems[component_name].components[self.entities[entity_id][components.component_index[component_name]]]
            return component
        except KeyError:
            raise KeyError(f"Component `{component_name}` or entity `{entity_id}` does not exist.")
    
    def get_property(self, entity_id, property):
        """Returns the property of that entity by reference"""
        return self.entity_props[entity_id][property]
    
    def set_property(self, entity_id, property, value):
        """Changes the value of an entity's property"""
        self.entity_props[entity_id][property] = value
    
    def add_action(self, action):
        """Put an action into the handler's queue and will be executed next cycle"""
        self.action_handler.add_action(action)
    
    def update_images(self, new_images_dict):
        """Updates the images dictionary with the given image dictionary"""
        self.images.update(new_images_dict)


class Camera:
    def __init__(self, game, target_id=None):
        self.game = game
        self.target_id = target_id
        self.target = None
        self.velocity = Vector2(0, 0)
        self.corner = Vector2(0, 0)
        self.width, self.height = self.game.screen.get_size()
        if self.target_id is not None:
            self.set_target(self.target_id)

    def set_target(self, target_id, jump=False):
        try:
            self.target = self.game.get_component(target_id, "transform")
            if jump:
                self.set_position(self.target)
        except KeyError:
            raise AttributeError("Camera target does not exist or does not have a transform component.")
    
    def set_position(self, position):
        self.corner = Vector2(position.x - self.width // 2, position.y - self.height // 2)
    
    def update(self):
        if self.target is not None:
            center = Vector2(self.corner.x + self.width // 2, self.corner.y + self.height // 2)
            self.velocity = self.velocity.lerp((Vector2(self.target.x, self.target.y) - center) * 4, 1)

            self.corner += self.velocity * self.game.dt
    
    def draw_grid(self):
        # Draw grid lines
        game = self.game
        grid_box_w, grid_box_h = (settings.GRID_SIZE, settings.GRID_SIZE)

        left_buffer = -self.corner.x % grid_box_w
        for x in range(round(self.width // grid_box_w) + 1):
            x_pos = left_buffer + x * grid_box_w
            pygame.draw.line(game.screen, colors.light_gray, (x_pos, 0), (x_pos, self.height))

        top_buffer = -self.corner.y % grid_box_h
        for y in range(round(self.height // grid_box_h) + 1):
            y_pos = top_buffer + y * grid_box_h
            pygame.draw.line(game.screen, colors.light_gray, (0, y_pos), (self.width, y_pos))


def show_fps(fps_font):
    clock.tick()
    #font = fps_font.render(f"Entities: {game.living_entities}, FPS: {round(clock.get_fps())}", False, colors.blue)
    font = fps_font.render(f"Health: {game.entity_props[0]['health']}", False, colors.blue)
    fps_rect = font.get_rect()
    fps_rect.topleft = 0, 0
    screen.blit(font, fps_rect)


if __name__ == "__main__":
    clock = pygame.time.Clock()
    FPS_FONT = pygame.font.SysFont("couriernew", 15)
    screen = pygame.display.set_mode(settings.SCREEN_SIZE, pygame.RESIZABLE)

    game = Game(screen, settings.COLLISION_GRID_WIDTH)
    pygame.event.set_allowed([KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    game.update_images(load_images())
    id = game.get_unique_id()
    game.add_action(actions.Spawn_Player(id, Vector2(300, 300), 0, 1, settings.PLAYER_MAX_SPEED, settings.PLAYER_ACCEL, settings.PLAYER_DECEL, settings.PLAYER_FRICTION))
    game.add_action(actions.Focus_Camera(id, True))
    enemy_id = game.get_unique_id()
    game.add_action(actions.Spawn_Enemy(enemy_id, Vector2(400, 500), 0, 1, settings.PLAYER_MAX_SPEED, settings.PLAYER_ACCEL, settings.PLAYER_DECEL, settings.PLAYER_FRICTION))
    game.add_action(actions.Start_Firing_Barrels(enemy_id))

    game.action_handler.handle_actions()

    while True:
        current_time = time.time()
        frame_time = current_time - game.last_time
        game.last_time = current_time
        game.accumulator += frame_time
        components.life_timer_sys.update()

        game.action_handler.get_player_input()
        components.controller_sys.update()
        components.barrel_manager_sys.update()


        while game.accumulator >= game.dt:
            game.get_component(enemy_id, "transform").rotation += 100 * game.dt
            components.physics_sys.update(game.dt)
            game.camera.update()
            components.collider_sys.update()
            game.action_handler.handle_actions()
            game.accumulator -= game.dt
        
        
        screen.fill(colors.white)
        game.camera.draw_grid()
        components.graphics_sys.update(screen)
        pygame.draw.rect(screen, colors.black, (1, 1, screen.get_width(), screen.get_height()), 3)
        show_fps(FPS_FONT)
        pygame.display.update()