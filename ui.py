import pygame

class Anchor:
    def __init__(self, anchor_point_string, pos):
        self.anchor_point_string = anchor_point_string
        self.pos = pos
    
    def move_rect(self, rect):
        if self.anchor_point_string == "top left":
            rect.topleft = self.pos
        elif self.anchor_point_string == "center":
            rect.center = self.pos
        elif self.anchor_point_string == "top right":
            rect.topright = self.pos
        elif self.anchor_point_string == "bottom left":
            rect.botleft = self.pos
        elif self.anchor_point_string == "bottom right":
            rect.botright = self.pos

class Text:
    def __init__(self, font_name, size, color, reflect_prop, anchor=Anchor("top left", (0, 0))):
        self.font_name = font_name
        self.size = size
        self.color = color
        self.reflect_prop = reflect_prop
        self.text = ""
        self.font = pygame.font.SysFont(self.font_name, self.size)
        self.surf = None
        self.rect = None
        self.anchor = anchor
        self.create_surf()
    
    def create_surf(self):
        self.surf = self.font.render(self.text, False, self.color)
        self.rect = self.surf.get_rect()
        self.anchor.move_rect(self.rect)
    
    def render(self, screen):
        screen.blit(self.surf, self.rect)
    
    def set_text(self, text):
        self.text = text
        self.create_surf()

class Button:
    def __init__(self, text_obj, anchor, outline_color, default_color, hover_color, pressed_color,
            change_on_click, padding=(0, 0), edge_rounding=2, outline_width=2):
        self.text = text_obj
        self.anchor = anchor
        self.rect = None
        self.padding = padding
        self.create_button()
        self.outline_color = outline_color
        self.default_color = default_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.func_or_var, self.args_or_val = change_on_click
        self.edge_rounding = edge_rounding
        self.outline_width = outline_width
        self.state = ""
    
    def create_button(self):
        rect = pygame.Rect(self.text.rect)
        rect.width = rect.width + 2 * self.padding[0]
        rect.height = rect.height + 2 * self.padding[1]
        self.anchor.move_rect(rect)
        self.text.rect.center = rect.center
        self.rect = rect
    
    def render(self, screen):
        if not self.state:
            pygame.draw.rect(screen, self.default_color, self.rect)
        elif self.state == "hovering":
            pygame.draw.rect(screen, self.hover_color, self.rect)
        elif self.state == "pressed":
            pygame.draw.rect(screen, self.pressed_color, self.rect)
        pygame.draw.rect(screen, self.outline_color, self.rect, self.outline_width, self.edge_rounding)
        self.text.render(screen)
    
    def check_event(self, event):
        if self.rect.collidepoint(event.pos):
            if event.type == pygame.MOUSEMOTION:
                if self.state != "pressed":
                    self.state = "hovering"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.state = "pressed"
                if callable(self.func_or_var):
                    if type(self.args_or_val) == tuple:
                        self.func_or_var(*self.args_or_val)
                    else:
                        self.func_or_var(self.args_or_val)
                else:
                    self.func_or_var = self.args_or_val
            elif event.type == pygame.MOUSEBUTTONUP:
                self.state = "hovering"
        else:
            self.state = ""

def update_fps_info(fps_id, game, clock):
    """This function just displays the current fps in the topleft corner."""
    
    clock.tick()
    if game.is_alive(fps_id):
        game.set_property(fps_id, "fps info", f"Entities: {game.get_living_entities()}, FPS: {round(clock.get_fps())}")

types = {
    "text":Text,
    "button":Button
}