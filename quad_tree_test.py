import sys
import pygame
import random
import time
import math
from pygame.locals import *
from pygame.math import Vector2
pygame.init()

tree_border = (1200, 750)
screen_resolution = (1200, 750)

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
        self.empty_children()
    
    def empty_children(self):
        self.children = {
            "tlt":None,
            "trt":None,
            "blt":None,
            "brt":None
        }
    
    def get_dist(self, a, b):
        return a.distance_to(b)
    
    def get_child(self, n):
        x, y = self.center
        child = ""
        if n.pos.x <= x:
            if n.pos.y <= y:
                child = "tlt"
            else:
                child = "blt"
        else:
            if n.pos.y <= y:
                child = "trt"
            else:
                child = "brt"
        return child
    
    def contains_possible_close_nodes(self, n, closest):
        x, y = n.pos
        t, b = self.tl, self.br
        tx, ty = t
        bx, by = b
        sides = []
        if x <= tx: sides.append(abs(x - tx))
        if x >= bx: sides.append(abs(x - bx))
        if y <= ty: sides.append(abs(y - ty))
        if y >= by: sides.append(abs(y - by))
        if len(sides) > 1:
            closest_side = min([n.pos.distance_to(t), n.pos.distance_to(b), n.pos.distance_to(Vector2(tx, by)), n.pos.distance_to(Vector2(bx, ty))])
        else:
            closest_side = min(sides)
        return closest_side < closest[0]
    
    def check_close_ids(self, n, n_child, closest=None, draw_time=None):
        # n_path is the child tree that holds n so it doesn't keep checking that tree
        if self.leaf:
            if draw_time:
                screen.fill((255,255,255))
                draw_search_node(self)
                root.draw()
                draw_red(n)
                if closest:
                    draw_green(closest[1])
                pygame.display.update()
                time.sleep(draw_time)
            dist = self.get_dist(self.node.pos, n.pos)
            if closest is None:
                return (dist, self.node)
            
            if dist < closest[0]:
                return (dist, self.node)
            else:
                return closest
        else:
            if draw_time:
                screen.fill((255,255,255))
                draw_search_node(self)
                root.draw()
                draw_red(n)
                if closest:
                    draw_green(closest[1])
                pygame.display.update()
                time.sleep(draw_time)
            for c in self.children.values():
                if c and c is not n_child:
                    if closest is None:
                        closest = c.check_close_ids(n, n_child, draw_time=draw_time)
                    else:
                        if c.contains_possible_close_nodes(n, closest):
                            closest = c.check_close_ids(n, n_child, closest, draw_time=draw_time)
            return closest
    
    def find_nearest_id(self, n, closest=None, draw_time=None):
        """Closest takes in (dist, node)"""
        if self.leaf:
            if self.node and self.node.id == n.id:
                if draw_time:
                    screen.fill((255,255,255))
                    root.draw()
                    draw_red(self.node)
                    pygame.display.update()
                    time.sleep(draw_time)
                return True, closest
            else:
                return False, closest
        else:
            child = self.get_child(n)
            found, closest = self.children[child].find_nearest_id(n, draw_time=draw_time)
            if not found:
                return False, closest
            else:
                closest = self.check_close_ids(n, self.children[child], closest, draw_time=draw_time)
                return True, closest
    
    def get_node_at_pos(self, pos):
        if self.leaf:
            return self
        else:
            child = ""
            if pos.x <= self.center.x:
                if pos.y <= self.center.y:
                    child = "tlt"
                else:
                    child = "blt"
            else:
                if pos.y <= self.center.y:
                    child = "trt"
                else:
                    child = "brt"
            if self.children[child] is not None:
                return self.children[child].get_node_at_pos(pos)
            else:
                return self

    def remove(self, n):
        if self.leaf:
            if self.node.id == n.id:
                self.node = None
                return True
            else:
                return False
        
        elif not self.leaf:
            child = self.get_child(n)
            
            total_children = sum([int(c is not None) for c in self.children.values()])
            if self.children[child].remove(n) and total_children > 1:
                self.children[child] = None
                total_children -= 1
            
            if total_children == 1:
                for c in self.children.values():
                    if c and c.leaf:
                        self.node = c.node
                        self.leaf = True
                        self.empty_children()
                        return False
            
            return False
    
    def insert(self, n):
        if self.node is None and self.leaf:  # Only occurs if it's the first insert
            self.node = n
            return

        if self.leaf:
            if self.node.pos.x <= self.center.x:
                if self.node.pos.y <= self.center.y:
                    self.children["tlt"] = N_Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), self.node, self)
                else:
                    self.children["blt"] = N_Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), self.node, self)
            else:
                if self.node.pos.y <= self.center.y:
                    self.children["trt"] = N_Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), self.node, self)
                else:
                    self.children["brt"] = N_Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), self.node, self)
            
            self.node = None
            self.leaf = False
        
        if abs(self.tl.x - self.br.x) > 2:
            if n.pos.x <= self.center.x:
                if n.pos.y <= self.center.y:
                    child = "tlt"
                    if self.children[child] == None:
                        self.children[child] = N_Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), n, self)
                        return
                    return self.children[child].insert(n)
                else:
                    child = "blt"
                    if self.children[child] == None:
                        self.children[child] = N_Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), n, self)
                        return
                    return self.children[child].insert(n)
            else:
                if n.pos.y <= self.center.y:
                    child = "trt"
                    if self.children[child] == None:
                        self.children[child] = N_Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), n, self)
                        return
                    return self.children[child].insert(n)
                else:
                    child = "brt"
                    if self.children[child] == None:
                        self.children[child] = N_Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), n, self)
                        return
                    return self.children[child].insert(n)
        else:
            return
    
    def draw(self):
        if kind == "border" or True:
            pygame.draw.rect(screen, (255, 0, 0), Rect(self.tl.x, self.tl.y, abs(self.tl.x - self.br.x), abs(self.tl.y - self.br.y)), 1)
        if not self.leaf:
            [self.children[child].draw() for child in ['tlt', 'trt', 'blt', 'brt'] if self.children[child]]
        elif self.node != None and kind == "point":
            pygame.draw.circle(screen, (0, 0, 255), (self.node.pos.x, self.node.pos.y), 2)

def draw_red(n):
    pygame.draw.circle(screen, (255, 0, 0), (n.pos.x, n.pos.y), 4)

def draw_green(n):
    pygame.draw.circle(screen, (0, 255, 0), (n.pos.x, n.pos.y), 4)

def draw_search_node(tree):
    pygame.draw.rect(screen, (245, 135, 135), (tree.tl, (tree.br.x - tree.tl.x, tree.br.y - tree.tl.y)))

if __name__ == "__main__":
    screen = pygame.display.set_mode(screen_resolution)
    screen.fill((255, 255, 255))
    root = N_Quad_Tree(Vector2(0, 0), Vector2(tree_border))
    id_on = 0
    kind = "point"
    last_time = time.time()
    nodes = []
    last_closest = []

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
            elif event.type == KEYDOWN and event.key == K_EQUALS:
                for i in range(10):
                    node = Node(Vector2(random.randint(0, tree_border[0]), random.randint(0, tree_border[1])), id_on)
                    id_on += 1
                    root.insert(node)
                    nodes.append(node)
            elif event.type == KEYDOWN and event.key == K_MINUS and len(nodes) > 0:
                node = random.choice(nodes)
                root.remove(node)
                nodes.remove(node)
                last_closest = []
            elif event.type == MOUSEBUTTONDOWN:
                node = root.get_node_at_pos(Vector2(pygame.mouse.get_pos()))
                if node.node:
                    exists, closest = root.find_nearest_id(node.node, draw_time=0.1)
                    if exists and closest is not None:
                        distance, closest_node = closest
                        print(distance)
                        last_closest = [node, closest_node]
                    else:
                        print("Something went wrong")


        screen.fill((255, 255, 255))
        mouse_node = None
        if len(nodes) > 1:
            mouse_node = root.get_node_at_pos(Vector2(pygame.mouse.get_pos()))
            if mouse_node.node is not None:
                exists, closest = root.find_nearest_id(mouse_node.node)
                if exists and closest is not None:
                    distance, closest_node = closest
                    draw_search_node(mouse_node)
                    last_closest = [mouse_node.node, closest_node]
                else:
                    print("Something went wrong again")
            else:
                last_closest = []

        root.draw()
        if last_closest != []:
            n1, n2 = last_closest
            draw_red(n1)
            draw_green(n2)
        pygame.display.update()