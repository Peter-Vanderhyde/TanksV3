from colors import *
from pygame.locals import *
RESOLUTION = (600, 600)
IMAGE_PATH = "Images/"
# [<name>, <alpha>, <colorkey>]
ASSETS = (("player_body", True, white), ("player_bullet", True), ("barrel", True, white))

# Settings
PLAYER_SPEED = 100
PLAYER_ACCEL = 0.1
PLAYER_MOVE_KEYS = {
    "left":K_a,
    "right":K_d,
    "up":K_w,
    "down":K_s
}