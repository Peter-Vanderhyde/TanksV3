import pygame
from pygame.math import Vector2

class GridManager:
    def __init__(self, cell_width, cell_height=None):
        """Takes the cell size for checking collisions"""
        self.cell_width = cell_width
        self.cell_height = cell_height or cell_width
        self.contents = {}
    
    def clear(self):
        self.contents = {}
    
    def hash(self, pos):
        """Returns the coordinates representing which cell that location is within."""
        p = Vector2(pos)
        return int(p.x / self.cell_width), int(p.y / self.cell_height)
    
    def get_cells_for_rect(self, rect):
        """Get every cell that the rectangle collides with."""
        min, max = self.hash(rect.topleft), self.hash(rect.bottomright)
        cells = []
        for x in range(min[0], max[0] + 1):
            for y in range(min[1], max[1] + 1):
                cells.append((x, y))
        return cells
    
    def insert_collider(self, collider):
        """Add the collider into the applicable cells under its collisions categories.
        These are all of the categories that the collider should check for collisions with.
        This allows only colliding with some objects, but not others."""
        transform = collider.transform_component
        origin = Vector2(transform.x, transform.y)
        rect = pygame.Rect(origin + collider.offset - Vector2(collider.radius), (collider.radius * 2, collider.radius * 2))
        new_cells = []
        for cell in self.get_cells_for_rect(rect):
            self.contents.setdefault(cell, set()).add(collider)
            new_cells.append(cell)
        collider.collision_cells = set(new_cells)
    
    def move_collider(self, collider):
        """Check to see if the rectangle is no longer in some cells, or needs to be added to others."""
        transform = collider.transform_component
        origin = Vector2(transform.x, transform.y)
        rect = pygame.Rect(origin + collider.offset - Vector2(collider.radius), (collider.radius * 2, collider.radius * 2))
        old_cells = collider.collision_cells
        new_cells = set(self.get_cells_for_rect(rect))
        if new_cells != old_cells:
            expired = old_cells - new_cells
            for cell in expired:
                self.contents[cell].discard(collider)
                if not self.contents[cell]: # No more colliders in the cell
                    del self.contents[cell]
            
            brand_new = new_cells - old_cells
            for cell in brand_new:
                self.contents.setdefault(cell, set()).add(collider)
            
        collider.collision_cells = set(new_cells)
    
    def remove_collider(self, collider):
        """The collider needs to be removed from all cells."""
        collision_cells = collider.collision_cells
        for cell in collision_cells:
            if collider in self.contents[cell]:
                self.contents[cell].discard(collider)
            if not self.contents[cell]:
                del self.contents[cell]
        
        collider.collision_cells = set()