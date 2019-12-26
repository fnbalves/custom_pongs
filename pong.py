import pygame
import time

WINDOW_HEIGHT = 300
WINDOW_WIDTH = 400
DONE = False
GAME_FREQUENCY = 40

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


class ControlledBrick():
    def __init__(self, screen, x=0, y=0, vx=10, size_x=40, size_y=5, 
        window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT, key_left=pygame.K_LEFT, key_right=pygame.K_RIGHT):
        self.x = x
        self.y = y
        self.vx = vx

        self.window_width = window_width
        self.window_height = window_height
        self.size_x = size_x
        self.size_y = size_y
        self.screen = screen
        self.key_left = key_left
        self.key_right = key_right
    
    def draw(self):
        pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, self.size_x, self.size_y))
    
    def update(self):
        pressed = pygame.key.get_pressed()
        
        if pressed[self.key_right] and (self.x + self.size_x) < self.window_width:
            self.x += self.vx
        
        if pressed[self.key_left] and self.x > 0:
            self.x -= self.vx
        
        self.draw()

class Ball:
    def __init__(self, screen, x=0, y=0, vx=10, vy=10, radius=10, window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.window_width = window_width
        self.window_height = window_height
        self.under_collision_x = False
        self.under_collision_y = False
        self.screen = screen

    def draw(self):
        pygame.draw.circle(self.screen, (0, 128, 255), (self.x, self.y), self.radius)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.draw()

    def reverse_vx(self):
        if not self.under_collision_x:
            self.vx *= -1
        self.under_collision_x = True

    def reverse_vy(self):
        if not self.under_collision_y:
            self.vy *= -1
        self.under_collision_y = True

    def check_frontiers(self):
        if (self.x - self.radius) < 0:
            self.reverse_vx()
        elif (self.x + self.radius) > self.window_width:
            self.reverse_vx()
        elif (self.y - self.radius) < 0:
            self.reverse_vy()
        elif (self.y + self.radius) > self.window_height:
            self.reverse_vy()
        else:
            self.under_collision_x = False
            self.under_collision_y = False

    def intersects_brick(self, brick):
        if (-1)*self.radius < (self.x - brick.x) < brick.size_x + self.radius and abs(self.y - brick.y) < self.radius:
            return True
        else:
            return False

    def check_brick(self, brick):
        if self.intersects_brick(brick):
            self.reverse_vy()

clock = pygame.time.Clock()
ball = Ball(screen, 0, 0, 5, 5, radius=3)
brick_1 = ControlledBrick(screen, 30, 250, size_x=80)
brick_2 = ControlledBrick(screen, 30, 50, size_x=80, key_left=pygame.K_a, key_right=pygame.K_d)

while not DONE:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            DONE = True

    screen.fill((0, 0, 0))

    ball.update()
    ball.check_frontiers()
    ball.check_brick(brick_1)
    ball.check_brick(brick_2)

    brick_1.update()
    brick_2.update()

    pygame.display.flip()
    clock.tick(GAME_FREQUENCY)

