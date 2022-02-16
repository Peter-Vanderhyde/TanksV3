from colors import *
from pygame.locals import *
import pygame
pygame.init()
monitor = pygame.display.Info()
SCREEN_SIZE = (monitor.current_w - 50, monitor.current_h - 75)
IMAGE_PATH = "Images/"
# [<name>, <alpha>, <colorkey>]
ASSETS = (("barrel", True, white),
("enemy_body", True, white),
("enemy_bullet", True, white),
("player_body", True, white),
("player_bullet", True, white))

# Settings
PLAYER_MAX_SPEED = 300
PLAYER_ACCEL = 0.15 # Speed up
PLAYER_DECEL = 0.1 # Slow down
PLAYER_FRICTION = 0.5 # Slipperiness
PLAYER_MOVE_KEYS = {
    "left":K_a,
    "right":K_d,
    "up":K_w,
    "down":K_s
}

BARREL_LENGTH = 42
BARREL_WIDTH = 21

GRID_SIZE = 100
COLLISION_GRID_WIDTH = 80