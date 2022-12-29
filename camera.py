import settings
import colors
from pygame import draw
from pygame.math import Vector2

class Camera:
    def __init__(self, game, target_id=None):
        self.game = game
        # The id of the entity is is looking at
        self.target_id = target_id
        if self.target_id is not None:
            self.set_target(self.target_id)
        else:
            # If the target is None, the camera will stay stationary where it is
            self.target = None
        self.velocity = Vector2(0, 0)
        # The top left corner of the camera/screen that everything is drawn based off of
        self.corner = Vector2(0, 0)
        self.width, self.height = self.game.screen.get_size()

    def set_target(self, target_id, jump=False):
        """
        Move the camera's center focal point to the position of the entity
        of the given id.
        """
        
        try:
            self.target = self.game.get_component(target_id, "transform")
            self.target_id = target_id
            if jump:
                self.set_position(self.target)
        except KeyError:
            raise AttributeError("Camera target does not exist or does not have a transform component.")
    
    def clear_target(self):
        """
        Reset the camera to not look at anything.
        """
        
        self.target_id = None
        self.target = None
    
    def set_position(self, position):
        """
        Position the center of the camera to the given position.
        """
        
        self.corner = Vector2(position.x - self.width // 2, position.y - self.height // 2)
    
    def update(self):
        """
        Move the camera to follow the target's position with linear interpolation
        to create a delayed panning effect.
        """
        
        if self.target is not None:
            center = Vector2(self.corner.x + self.width // 2, self.corner.y + self.height // 2)
            self.velocity = self.velocity.lerp((Vector2(self.target.x, self.target.y) - center) * settings.CAMERA_PAN_SPEED, 1)

            self.corner += self.velocity * self.game.dt
    
    def draw_grid(self):
        """
        This function draws the background lines of the grid that move as the
        player does.
        """

        game = self.game
        grid_box_w, grid_box_h = (settings.GRID_SIZE, settings.GRID_SIZE)

        left_buffer = -self.corner.x % grid_box_w
        for x in range(round(self.width // grid_box_w) + 1):
            x_pos = left_buffer + x * grid_box_w
            draw.line(game.screen, colors.light_gray, (x_pos, 0), (x_pos, self.height))

        top_buffer = -self.corner.y % grid_box_h
        for y in range(round(self.height // grid_box_h) + 1):
            y_pos = top_buffer + y * grid_box_h
            draw.line(game.screen, colors.light_gray, (0, y_pos), (self.width, y_pos))