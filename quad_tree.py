import sys
import pygame
import random
import time
from pygame.locals import *
from pygame.math import Vector2
pygame.init()

tree_border = (600, 600)
screen_resolution = (600, 600)

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Node:
    def __init__(self, pos, id):
        self.pos = pos
        self.id = id

class N_Quad_Tree:
    def __init__(self, top_left, bot_right, node=None, parent=None):
        self.node = node
        self.parent = parent
        self.leaf = True
        self.tl = top_left
        self.br = bot_right
        self.center = Vector2((self.tl.x + self.br.x) // 2, (self.tl.y + self.br.y) // 2)
        self.tlt = None
        self.trt = None
        self.blt = None
        self.brt = None
    
    def insert(self, n):
        if self.node == None and self.leaf:  # Only occurs if it's the first insert
            self.node = n
            return

        if self.leaf:
            if self.node.pos.x <= self.center.x:
                if self.node.pos.y <= self.center.y:
                    self.tlt = N_Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), self.node, self)
                else:
                    self.blt = N_Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), self.node, self)
            else:
                if self.node.pos.y <= self.center.y:
                    self.trt = N_Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), self.node, self)
                else:
                    self.brt = N_Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), self.node, self)
            
            self.node = None
            self.leaf = False
        
        if abs(self.tl.x - self.br.x) > 2:
            if n.pos.x <= self.center.x:
                if n.pos.y <= self.center.y:
                    if self.tlt == None:
                        self.tlt = N_Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), n, self)
                        return
                    return self.tlt.insert(n)
                else:
                    if self.blt == None:
                        self.blt = N_Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), n, self)
                        return
                    return self.blt.insert(n)
            else:
                if n.pos.y <= self.center.y:
                    if self.trt == None:
                        self.trt = N_Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), n)
                        return
                    return self.trt.insert(n)
                else:
                    if self.brt == None:
                        self.brt = N_Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), n)
                        return
                    return self.brt.insert(n)
        else:
            return
    
    def draw(self):
        if kind == "border" or True:
            pygame.draw.rect(screen, (255, 0, 0), Rect(self.tl.x, self.tl.y, abs(self.tl.x - self.br.x), abs(self.tl.y - self.br.y)), 1)
        if not self.leaf:
            if self.tlt:
                self.tlt.draw()
            if self.blt:
                self.blt.draw()
            if self.trt:
                self.trt.draw()
            if self.brt:
                self.brt.draw()
        elif self.node != None and kind == "point":
            pygame.draw.circle(screen, (0, 0, 255), (self.node.pos.x, self.node.pos.y), 2)


if __name__ == "__main__":
    screen = pygame.display.set_mode(screen_resolution)
    screen.fill((255, 255, 255))
    root = N_Quad_Tree(Vector2(0, 0), Vector2(tree_border))
    id_on = 0
    kind = "point"
    last_time = time.time()

    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                if kind == "border":
                    kind = "point"
                else:
                    kind = "border"
        
        if time.time() - last_time >= 0.0001:
            node = Node(Vector2(random.randint(0, tree_border[0]), random.randint(0, tree_border[1])), id_on)
            id_on += 1
            root.insert(node)
            last_time = time.time()

        screen.fill((255, 255, 255))
        root.draw()
        pygame.display.update()