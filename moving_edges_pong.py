import pygame
import time
import math
import random

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500
DONE = False
GAME_FREQUENCY = 70

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

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
    def __init__(self, screen, x=0, y=0, vx=10, vy=10, radius=10, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
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

        new_velocity = Vector(0.0, 0.0)
        velocities = []

        some_activated = False

        for checker in self.checkers:
           checker.update()
            

class ControlledBrick():
    def __init__(self, collision_group, screen, x=0, y=0, vx=10, size_x=40, size_y=5, 
        window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT):
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
    def __init__(self, collision_group, screen, corner1, corner2, corner3, corner4, player1, player2):
        self.collision_group = collision_group
        self.screen = screen
        self.player1 = player1
        self.player2 = player2

        self.corner1 = corner1
        self.corner2 = corner2
        self.corner3 = corner3
        self.corner4 = corner4

        self.lines = []
        self.lines.append([CollisionLine(self.screen, corner1.corner.x, corner1.corner.y, corner2.corner.x, corner2.corner.y, 
            color=(255,0,0)), player1])
        self.lines.append([CollisionLine(self.screen, corner2.corner.x, corner2.corner.y, corner3.corner.x, corner3.corner.y, color=(255,0,0)), None])
        self.lines.append([CollisionLine(self.screen, corner3.corner.x, corner3.corner.y, corner4.corner.x, corner4.corner.y, 
            color=(255,0,0)), player2])
        self.lines.append([CollisionLine(self.screen, corner4.corner.x, corner4.corner.y, corner1.corner.x, corner1.corner.y, color=(255,0,0)), None])

        for line in self.lines:
            self.collision_group.add_line(line[0], line[1])

    @staticmethod
    def update_line(line, x1, y1, x2, y2):
        line.x1 = x1
        line.y1 = y1
        line.x2 = x2
        line.y2 = y2
        line.update_params()

    def update(self):
        MovingFrontiers.update_line(self.lines[0][0], self.corner1.corner.x, self.corner1.corner.y, self.corner2.corner.x, self.corner2.corner.y)
        MovingFrontiers.update_line(self.lines[1][0], self.corner2.corner.x, self.corner2.corner.y, self.corner3.corner.x, self.corner3.corner.y)
        MovingFrontiers.update_line(self.lines[2][0], self.corner3.corner.x, self.corner3.corner.y, self.corner4.corner.x, self.corner4.corner.y)
        MovingFrontiers.update_line(self.lines[3][0], self.corner4.corner.x, self.corner4.corner.y, self.corner1.corner.x, self.corner1.corner.y)

clock = pygame.time.Clock()

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 15)

ball = Ball(screen, 200, 200, 3, 3, radius=7)
c_group = CollisionLineGroup(ball, verbose=True)
SCALE = 40

wp1 = MovingCorner(screen, 2*SCALE, 2*SCALE, SCALE, SCALE, 1, 3)
wp2 = MovingCorner(screen, WINDOW_WIDTH - 2*SCALE, 2*SCALE, SCALE, SCALE, 3, 2)
wp3 = MovingCorner(screen, WINDOW_WIDTH - 2*SCALE, WINDOW_HEIGHT - 2*SCALE, SCALE, SCALE, 3, 1)
wp4 = MovingCorner(screen, 2*SCALE, WINDOW_HEIGHT - 2*SCALE, SCALE, SCALE, 2, 2)

def player_died(name):
    screen.fill((0, 0, 0))
    textsurface = myfont.render('Player %s lost!!!' % name, False, (255, 0, 0))
    screen.blit(textsurface, (150, 20))
    pygame.display.flip()

    time.sleep(2)

    player1.life = 10
    player2.life = 10
    ball.v.x = 3
    ball.v.y = 3
    ball.x = 200
    ball.y = 200

player1 = Player('player 1', death_callback=player_died)
player2 = Player('player 2', death_callback=player_died)

mf = MovingFrontiers(c_group, screen, wp1, wp2, wp3, wp4, player1, player2)
brick1 = ControlledBrick(c_group, screen, 150, WINDOW_HEIGHT - 150, size_x=80, key_left=pygame.K_j, key_right=pygame.K_l)
brick2 = ControlledBrick(c_group, screen, 150, 150, size_x=80, key_left=pygame.K_a, key_right=pygame.K_d)

obj_updater = ObjectUpdater()

obj_updater.add_object(brick1)
obj_updater.add_object(brick2)
obj_updater.add_object(wp1)
obj_updater.add_object(wp2)
obj_updater.add_object(wp3)
obj_updater.add_object(wp4)
obj_updater.add_object(mf)
obj_updater.add_object(ball)
obj_updater.add_object(c_group)

#c_group.add_line(CollisionLine(screen, 0, 0, 0, 300, color=(255,0,0)))
#c_group.add_line(CollisionLine(screen, 0, 300, 200, 400, color=(255,0,0)))
#c_group.add_line(CollisionLine(screen, 200, 400, 250, 20, color=(255,0,0)))
#c_group.add_line(CollisionLine(screen, 250, 20, 0, 0, color=(255,0,0)))

while not DONE:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            DONE = True

    screen.fill((0, 0, 0))
    textsurface = myfont.render('Player 1: %d | Player 2: %d' % (player1.life, player2.life), False, (255, 0, 0))
    screen.blit(textsurface, (150, 20))

    obj_updater.update()
    
    pygame.display.flip()
    clock.tick(GAME_FREQUENCY)
    print()

