import sys
import time
import random
import pygame
from pygame.locals import *
from pygame.math import Vector2
pygame.init()



class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Node:
    def __init__(self, id, pos=Point()):
        self.id = id
        self.pos = pos

class Quad_Tree:
    def __init__(self, tl=Point(), br=Point(), na=None, nb=None):
        self.tl = tl
        self.br = br
        self.center = Point((tl.x + br.x) // 2, (tl.y + br.y) // 2)
        self.na = na
        self.nb = nb
        self.leaf = True
        self.tlt = None
        self.blt = None
        self.trt = None
        self.brt = None
    
    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), (self.tl.x, self.tl.y, abs(self.tl.x - self.br.x), abs(self.tl.y - self.br.y)), 1)
        if self.leaf:
            if self.na:
                pygame.draw.circle(screen, (0, 0, 255), (self.na.pos.x, self.na.pos.y), 2)
            if self.nb:
                pygame.draw.circle(screen, (0, 0, 255), (self.nb.pos.x, self.nb.pos.y), 2)
        else:
            if self.tlt:
                self.tlt.draw()
            if self.blt:
                self.blt.draw()
            if self.trt:
                self.trt.draw()
            if self.brt:
                self.brt.draw()
    
    def push_to_leaf(self, node):
        pos = node.pos
        if pos.x < self.center.x:
            if pos.y < self.center.y:
                if self.tlt == None:
                    self.tlt = Quad_Tree(self.tl, self.center, node)
                    return
                self.tlt.insert(node)
                return
            else:
                if self.blt == None:
                    self.blt = Quad_Tree(Point(self.tl.x, self.center.y), Point(self.center.x, self.br.y), node)
                    return
                self.blt.insert(node)
                return
        else:
            if pos.y < self.center.y:
                if self.trt == None:
                    self.trt = Quad_Tree(Point(self.center.x, self.tl.y), Point(self.br.x, self.center.y), node)
                    return
                self.trt.insert(node)
                return
            else:
                if self.brt == None:
                    self.brt = Quad_Tree(self.center, self.br, node)
                    return
                self.brt.insert(node)
                return
    
    def insert(self, node):
        if self.leaf:
            if self.na == None:
                self.na = node
                return
            elif self.nb == None:
                self.nb = node
                return
            self.leaf = False
            self.push_to_leaf(node)
            self.push_to_leaf(self.na)
            self.na = None
            self.push_to_leaf(self.nb)
            self.nb = None
            return
        else:
            self.push_to_leaf(node)



if __name__ == "__main__":
    resolution = (600, 600)
    screen = pygame.display.set_mode(resolution)
    q_tree = Quad_Tree(Point(), Point(resolution[0], resolution[1]))
    next_id = 0
    last_time = time.time()

    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                q_tree.insert(Node(next_id, Point(pos[0], pos[1])))
                next_id += 1
        
        if time.time() - last_time >= 0.1:
            pos = (random.randint(0, resolution[0]), random.randint(0, resolution[1]))
            q_tree.insert(Node(next_id, Point(pos[0], pos[1])))
            next_id += 1
            last_time = time.time()
        
        screen.fill((255, 255, 255))
        q_tree.draw()
        pygame.display.update()