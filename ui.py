from tkinter import font
import pygame

class Font:
    def __init__(self, font_name, size, color, text="", pos=(0, 0)):
        self.font_name = font_name
        self.size = size
        self.color = color
        self.text = text
        self.font = None
        self.surf = None
        self.rect = None
        self.create_font()
        self.render()
    
    def create_font(self):
        self.font = pygame.font.SysFont(self.font_name, self.size)
    
    def render(self):
        self.surf = self.font.render(self.text, False, self.color)
        self.rect = self.surf.get_rect()
        self.rect.topleft = 0, 0
    
    def set_text(self, text):
        self.text = text
        self.render()


def show_fps(fps_font, game, clock):
    """This function just displays the current fps in the topleft corner."""
    
    clock.tick()
    fps_font.set_text(f"Entities: {game.living_entities}, FPS: {round(clock.get_fps())}")
    fps_font.rect.topleft = 6, 0
    game.screen.blit(fps_font.surf, fps_font.rect)