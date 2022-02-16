import pygame
from pygame.math import Vector2

class Grid_Manager:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}
    
    def clear(self):
        self.contents = {}
    
    def hash(self, pos):
        p = Vector2(pos)
        return int(p.x / self.cell_size), int(p.y / self.cell_size)
    
    def get_cells_for_rect(self, rect):
        min, max = self.hash(rect.topleft), self.hash(rect.bottomright)
        cells = []
        for x in range(min[0], max[0] + 1):
            for y in range(min[1], max[1] + 1):
                cells.append((x, y))
        return cells
    
    def insert_collider(self, collider):
        transform = collider.transform_component
        origin = Vector2(transform.x, transform.y)
        rect = pygame.Rect(origin + collider.offset - Vector2(collider.radius), (collider.radius * 2, collider.radius * 2))
        new_cells = []
        for cell in self.get_cells_for_rect(rect):
            self.contents.setdefault(cell, []).append(collider)
            new_cells.append(cell)
        collider.collision_cells = set(new_cells)
    
    def move_collider(self, collider):
        transform = collider.transform_component
        origin = Vector2(transform.x, transform.y)
        rect = pygame.Rect(origin + collider.offset - Vector2(collider.radius), (collider.radius * 2, collider.radius * 2))
        old_cells = list(collider.collision_cells)
        old_cells.sort()
        new_cells = self.get_cells_for_rect(rect)
        new_cells.sort()
        if new_cells != old_cells:
            for cell in old_cells:
                if cell not in new_cells:
                    self.contents[cell].remove(collider)
                    if self.contents[cell] == []:
                        del self.contents[cell]
            for cell in new_cells:
                if cell not in self.contents or collider not in self.contents[cell]:
                    self.contents.setdefault(cell, []).append(collider)
        collider.collision_cells = set(new_cells)
    
    def remove_collider(self, collider):
        collision_cells = collider.collision_cells
        for cell in collision_cells:
            if collider in self.contents[cell]:
                self.contents[cell].remove(collider)
            if self.contents[cell] == []:
                del self.contents[cell]
        collider.collision_cells = set()