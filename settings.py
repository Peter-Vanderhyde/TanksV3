from colors import *
from pygame.locals import *
import pygame
pygame.init()
monitor = pygame.display.Info()
SCREEN_SIZE = (monitor.current_w - 50, monitor.current_h - 75)
IMAGE_PATH = "Images/"
# [<name>, <alpha>, <colorkey>]
ASSETS = (("barrel", True, white), ("enemy_body", True), ("enemy_bullet", True), ("player_body", True), ("player_bullet", True))

# Settings
PLAYER_MAX_SPEED = 300
PLAYER_ACCEL = 0.1
PLAYER_DECEL = 0.07
PLAYER_FRICTION = 0.5
PLAYER_MOVE_KEYS = {
    "left":K_a,
    "right":K_d,
    "up":K_w,
    "down":K_s
}

BARREL_LENGTH = 40
BARREL_WIDTH = 20

GRID_SIZE = 100