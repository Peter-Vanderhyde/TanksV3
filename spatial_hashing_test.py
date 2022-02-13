from pygame.math import Vector2

class Hashing_Manager:
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
    
    def insert_id_for_rect(self, id, rect):
        new_cells = []
        for cell in self.get_cells_for_rect(rect):
            self.contents.setdefault(cell, []).append(id)
            new_cells.append(cell)
        return set(new_cells)
    
    def move_id_for_rect(self, id, old_cells, rect):
        old_cells = list(old_cells)
        new_cells = self.get_cells_for_rect(rect)
        if new_cells != old_cells:
            for cell in old_cells:
                if cell not in new_cells:
                    self.contents[cell].remove(id)
            for cell in new_cells:
                if id not in self.contents.setdefault(cell, []):
                    self.contents[cell].append(id)
        return set(new_cells)
    
    def remove_id(self, id, rect):
        for cell in self.get_cells_for_rect(rect):
            self.contents[cell].remove(id)
            if self.contents[cell] == []:
                del self.contents[cell]
        return set()