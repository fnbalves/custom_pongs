import pygame
import math
import random

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def dot_prod(v1, v2):
    return v1.x*v2.x + v1.y*v2.y

def norm(v1):
    return math.sqrt(v1.x ** 2 + v1.y ** 2)

def multiply_v(c, v1):
    v2 = Vector(c*v1.x, c*v1.y)
    return v2

def sum_v(v1, v2):
    v3 = Vector(v1.x + v2.x, v1.y + v2.y)
    return v3

class CollisionLine:
    def __init__(self, screen, x1, y1, x2, y2, color=(0, 255, 0)):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.screen = screen

        max_x = max(self.x1, self.x2)
        min_x = min(self.x1, self.x2)

        max_y = max(self.y1, self.y2)
        min_y = min(self.y1, self.y2)

        self.vect = Vector((max_x - min_x), (max_y - min_y))
        self.norm = norm(self.vect)
        self.basic_vect = multiply_v(1/self.norm, self.vect)

        self.update_params()
    
    def update_params(self):
        self.m = None

        if self.x1 != self.x2:
            self.m = float(self.y2 - self.y1)/float(self.x2 - self.x1)

            self.c = float(self.y1*self.x2 - self.y2*self.x1)/float(self.x2 - self.x1)
        else:
            self.c = self.x1

    def draw(self):
        pygame.draw.line(self.screen, self.color, (int(self.x1), int(self.y1)), (int(self.x2), int(self.y2)))

    @staticmethod
    def __solve_baskara(a, b, c):
        delta = b**2 - 4*a*c
        if delta < 0:
            return None
        else:
            x1 = (-b + math.sqrt(delta))/(2*a)
            x2 = (-b - math.sqrt(delta))/(2*a)
            return [x1, x2]

    def intersection_with_ball(self, ball):
        if self.m is not None:
            a = (1 + self.m ** 2)
            b = 2*self.m*(self.c - ball.y) -2*ball.x
            c = ball.x ** 2 + (self.c - ball.y)**2 - ball.radius**2
            
            X = CollisionLine.__solve_baskara(a, b, c)
            if X is None:
                return None

            Y = [self.m*x + self.c for x in X]
            return [a for a in zip(X, Y)]
        else:
            F = ball.radius ** 2 - (self.c - ball.x)**2
            if F < 0:
                return None
            Y = [ball.y + math.sqrt(F), ball.y - math.sqrt(F)]
            return [a for a in zip([self.c, self.c], Y)]

    def point_between(self, point):
        max_x = max(self.x1, self.x2)
        min_x = min(self.x1, self.x2)

        max_y = max(self.y1, self.y2)
        min_y = min(self.y1, self.y2)

        return (min_x <= point[0] <= max_x) and (min_y <= point[1] <= max_y)

    def collision_with_ball(self, ball):
        inter = self.intersection_with_ball(ball)
        if inter is None:
            return False
        ret = any([self.point_between(p) for p in inter])

        return ret

    def revert_velocity(self, v_vect):
        v_parallel = multiply_v(dot_prod(v_vect, self.basic_vect), self.basic_vect)
        v_perp = sum_v(v_vect, multiply_v(-1, v_parallel))
        new_velocity = sum_v(v_parallel, multiply_v(-1, v_perp))
        
        return new_velocity

class Player:
    def __init__(self, name, initial_life=10, death_callback=None):
        self.name = name
        self.life = initial_life
        self.death_callback = death_callback

    def take_hit(self):
        self.life -= 1
        if self.life == 0:
            if self.death_callback is not None:
                self.death_callback(self.name)

class CollisionChecker:
    def __init__(self, line, ball, player=None):
        self.line = line
        self.ball = ball
        self.has_intersection = False
        self.player = player

    def update(self):
        inter = self.line.collision_with_ball(self.ball)
        
        if inter and not self.has_intersection:
            reversed_velocity = self.line.revert_velocity(self.ball.v)
            self.has_intersection = True
            self.ball.v = reversed_velocity
            if self.player is not None:
                self.player.take_hit()

        elif not inter:
            self.has_intersection = False
            
class Ball:
    def __init__(self, screen, x=0, y=0, vx=10, vy=10, radius=10, window_width=500, window_height=500):
        self.x = x
        self.y = y
        self.v = Vector(vx, vy)
        self.radius = radius
        self.window_width = window_width
        self.window_height = window_height
        self.screen = screen

    def draw(self):
        pygame.draw.circle(self.screen, (0, 128, 255), (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.v.x
        self.y += self.v.y
        self.draw()

class CollisionLineGroup:
    def __init__(self, ball, verbose=False):
        self.ball = ball
        self.lines = []
        self.checkers = []
        self.verbose=verbose
        self.has_intersection = False

    def add_line(self, line, player=None):
        self.lines.append(line)
        if player is not None:
            self.checkers.append(CollisionChecker(line, self.ball, player=player))
        else:
            self.checkers.append(CollisionChecker(line, self.ball))
    
    def update(self):
        for line in self.lines:
            line.draw()

        some_activated = False

        for checker in self.checkers:
           checker.update()
            

class ControlledBrick():
    def __init__(self, collision_group, screen, x=0, y=0, vx=10, size_x=40, size_y=5, 
        window_width=500, window_height=500, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT):
        self.x = x
        self.y = y
        self.vx = vx

        self.window_width = window_width
        self.window_height = window_height
        self.size_x = size_x
        self.size_y = size_y
        self.collision_group = collision_group
        self.key_left = key_left
        self.key_right = key_right
    
        self.border_lines = []
        self.border_lines.append(CollisionLine(screen, x, y, x + size_x, y))
        self.border_lines.append(CollisionLine(screen, x, y + size_y, x + size_x, y + size_y))
        self.border_lines.append(CollisionLine(screen, x, y, x, y+size_y))
        self.border_lines.append(CollisionLine(screen, x + size_x, y, x + size_x, y + size_y))

        for line in self.border_lines:
            self.collision_group.add_line(line)
    
    def update(self):
        pressed = pygame.key.get_pressed()
        
        if pressed[self.key_right] and (self.x + self.size_x) < self.window_width:
            for line in self.border_lines:
                line.x1 += self.vx
                line.x2 += self.vx
                line.update_params()

        if pressed[self.key_left] and self.x > 0:
            for line in self.border_lines:
                line.x1 -= self.vx
                line.x2 -= self.vx
                line.update_params()


class ObjectUpdater:
    def __init__(self):
        self.objects = []
    
    def add_object(self, obj):
        self.objects.append(obj)

    def update(self):
        for obj in self.objects:
            obj.update()


class MovingCorner:
    def __init__(self, screen, x, y, offset_x, offset_y, vx=1, vy=3):
        self.corner = Ball(screen, x, y, vx, vy, radius=2)
        self.limits = []
        self.screen = screen

        self.limits.append(CollisionLine(self.screen, x - offset_x, y - offset_y, x + offset_x, y - offset_y, color=(255,255,0)))
        self.limits.append(CollisionLine(self.screen, x - offset_x, y + offset_y, x + offset_x, y + offset_y, color=(255,255,0)))
        self.limits.append(CollisionLine(self.screen, x - offset_x, y - offset_y, x - offset_x, y + offset_y, color=(255,255,0)))
        self.limits.append(CollisionLine(self.screen, x + offset_x, y - offset_y, x + offset_x, y + offset_y, color=(255,255,0)))

        self.collision_group = CollisionLineGroup(self.corner)
        for line in self.limits:
            self.collision_group.add_line(line)
    
    def update(self):
        self.corner.update()
        self.collision_group.update()

class MovingFrontiers:
    def __init__(self, collision_group, screen, m_corner1,  m_corner2, m_corner3, m_corner4, player1, player2):
        self.collision_group = collision_group
        self.screen = screen
        self.player1 = player1
        self.player2 = player2

        self.corner1 = m_corner1.corner
        self.corner2 = m_corner2.corner
        self.corner3 = m_corner3.corner
        self.corner4 = m_corner4.corner

        self.lines = []
        self.players = [self.player1, None, self.player2, None]

        self.lines.append(CollisionLine(self.screen, self.corner1.x, self.corner1.y, self.corner2.x, self.corner2.y, color=(255,0,0)))
        self.lines.append(CollisionLine(self.screen, self.corner2.x, self.corner2.y, self.corner3.x, self.corner3.y, color=(255,0,0)))
        self.lines.append(CollisionLine(self.screen, self.corner3.x, self.corner3.y, self.corner4.x, self.corner4.y, color=(255,0,0)))
        self.lines.append(CollisionLine(self.screen, self.corner4.x, self.corner4.y, self.corner1.x, self.corner1.y, color=(255,0,0)))

        for player, line in zip(self.players, self.lines):
            self.collision_group.add_line(line, player)

    @staticmethod
    def update_line(line, x1, y1, x2, y2):
        line.x1 = x1
        line.y1 = y1
        line.x2 = x2
        line.y2 = y2
        line.update_params()

    def update(self):
        MovingFrontiers.update_line(self.lines[0], self.corner1.x, self.corner1.y, self.corner2.x, self.corner2.y)
        MovingFrontiers.update_line(self.lines[1], self.corner2.x, self.corner2.y, self.corner3.x, self.corner3.y)
        MovingFrontiers.update_line(self.lines[2], self.corner3.x, self.corner3.y, self.corner4.x, self.corner4.y)
        MovingFrontiers.update_line(self.lines[3], self.corner4.x, self.corner4.y, self.corner1.x, self.corner1.y)
