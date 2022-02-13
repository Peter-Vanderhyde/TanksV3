import sys
import os
import pygame
from pygame.locals import *
from pygame.math import Vector2
pygame.init()

class Hashing_Manager:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}
    
    def clear(self):
        self.contents = {}
    
    def hash(self, pos):
        p = Vector2(pos)
        return int(p.x / self.cell_size), int(p.y / self.cell_size)
    
    def insert_id_at_pos(self, id, pos):
        self.contents.setdefault(self.hash(pos), []).append(id)
    
    def get_cells_for_rect(self, rect):
        min, max = self.hash(rect.topleft), self.hash(rect.bottomright)
        cells = []
        for x in range(min[0], max[0] + 1):
            for y in range(min[1], max[1] + 1):
                cells.append((x, y))
    
    def insert_id_for_rect(self, id, rect):
        for cell in self.get_cells_for_rect(rect):
            self.contents.setdefault(cell, []).append(id)
    
    def move_id_for_rect(self, id, rect):
        for cell in self.get_cells_for_rect(rect):
            if id not in self.contents.setdefault(cell, []):
                self.contents[cell].append(id)
    
    def remove_id(self, id, rect):
        for cell in self.get_cells_for_rect(rect):
            self.contents[cell].remove(id)
            if self.contents[cell] == []:
                del self.contents[cell]