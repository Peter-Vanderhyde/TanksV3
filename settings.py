from colors import *
from pygame.locals import *
import pygame
pygame.init()
monitor = pygame.display.Info()
SCREEN_SIZE = (monitor.current_w - 50, monitor.current_h - 75)
IMAGE_PATH = "images/"
ANIMATION_PATH = "animations/"
# (<name>, <alpha>, <colorkey>)
ASSETS = (
    ("barrel", True, white),
    ("body_enemy", True, white),
    ("bullet_enemy", True, white),
    ("body_player", True, white),
    ("bullet_player", True, white),
    ("particle_enemy", True, white),
    ("particle_player", True, white),
    ("particle_2_enemy", True, white),
    ("particle_2_player", True, white),
    ("particle_3_enemy", True, white),
    ("particle_3_player", True, white),
    ("square_small", True)
)

PARTICLES = {
    'body_enemy': ['particle_enemy', 'particle_2_enemy'],
    'bullet_enemy': ['particle_2_enemy', 'particle_3_enemy'],
    'body_player': ['particle_player', 'particle_2_player'],
    'bullet_player': ['particle_2_player', 'particle_3_player'],
    "barrel":["barrel"]
}

COLLISION_CATEGORIES = ["projectiles", "actors", "shapes", "particles"]

# Settings
PLAYER_MAX_SPEED = 300
PLAYER_ACCEL = 0.15 # Speed up /|\ bigger number speeds up faster
PLAYER_DECEL = 0.1 # Slow down /|\ bigger number slows down faster
PLAYER_FRICTION = 0.5 # Slipperiness /|\ bigger number means less sliding
PLAYER_MOVE_KEYS = {
    "left":K_a,
    "right":K_d,
    "up":K_w,
    "down":K_s
}

PARTICLE_FRICTION = 0.2

BARREL_LENGTH = 42
BARREL_WIDTH = 21

GRID_SIZE = 100
COLLISION_GRID_WIDTH = 80