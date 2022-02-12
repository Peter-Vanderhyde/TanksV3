from pygame.math import Vector2

class Node:
    def __init__(self, id, pos):
        self.id = id
        self.pos = pos

class Quad_Tree:
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
    
    def remove(self, n):
        if self.node is None and self.leaf:
            return False
        
        elif self.leaf:
            if self.node.id == n.id:
                self.node = None
                return True
            else:
                return False
        
        elif self.node is None and not self.leaf:
            child = ""
            if n.pos.x <= self.center.x:
                if n.pos.y <= self.center.y:
                    child = "tlt"
                else:
                    child = "blt"
            else:
                if n.pos.y <= self.center.y:
                    child = "trt"
                else:
                    child = "brt"
            
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
                    self.children["tlt"] = Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), self.node, self)
                else:
                    self.children["blt"] = Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), self.node, self)
            else:
                if self.node.pos.y <= self.center.y:
                    self.children["trt"] = Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), self.node, self)
                else:
                    self.children["brt"] = Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), self.node, self)
            
            self.node = None
            self.leaf = False
        
        if abs(self.tl.x - self.br.x) > 2:
            if n.pos.x <= self.center.x:
                if n.pos.y <= self.center.y:
                    child = "tlt"
                    if self.children[child] == None:
                        self.children[child] = Quad_Tree(Vector2(self.tl.x, self.tl.y), Vector2(self.center.x+1, self.center.y+1), n, self)
                        return
                    return self.children[child].insert(n)
                else:
                    child = "blt"
                    if self.children[child] == None:
                        self.children[child] = Quad_Tree(Vector2(self.tl.x, self.center.y), Vector2(self.center.x+1, self.br.y), n, self)
                        return
                    return self.children[child].insert(n)
            else:
                if n.pos.y <= self.center.y:
                    child = "trt"
                    if self.children[child] == None:
                        self.children[child] = Quad_Tree(Vector2(self.center.x, self.tl.y), Vector2(self.br.x, self.center.y+1), n)
                        return
                    return self.children[child].insert(n)
                else:
                    child = "brt"
                    if self.children[child] == None:
                        self.children[child] = Quad_Tree(Vector2(self.center.x, self.center.y), Vector2(self.br.x, self.br.y), n)
                        return
                    return self.children[child].insert(n)
        else:
            return