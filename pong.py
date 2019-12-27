import pygame
import time

from pong_classes import *

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500
DONE = False
GAME_FREQUENCY = 70
OFFSET = 20
INITIAL_LIFE = 5

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pygame.time.Clock()

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 15)

ball = Ball(screen, 200, 200, 3, 3, radius=7)

def player_died(name):
    screen.fill((0, 0, 0))
    textsurface = myfont.render('Player %s lost!!!' % name, False, (255, 0, 0))
    screen.blit(textsurface, (170, 20))
    pygame.display.flip()

    time.sleep(2)

    player1.life = INITIAL_LIFE
    player2.life = INITIAL_LIFE
    ball.v.x = 3
    ball.v.y = 3
    ball.x = 200
    ball.y = 200

player1 = Player('player 1', INITIAL_LIFE, death_callback=player_died)
player2 = Player('player 2', INITIAL_LIFE, death_callback=player_died)

c_group = CollisionLineGroup(ball, verbose=True)
c_group.add_line(CollisionLine(screen, OFFSET, OFFSET, WINDOW_WIDTH - OFFSET, OFFSET, color=(255,0,0)), player=player1)
c_group.add_line(CollisionLine(screen, WINDOW_WIDTH - OFFSET, OFFSET, WINDOW_WIDTH - OFFSET, WINDOW_HEIGHT - OFFSET, color=(255,0,0)))
c_group.add_line(CollisionLine(screen, WINDOW_WIDTH - OFFSET, WINDOW_HEIGHT - OFFSET, OFFSET, WINDOW_HEIGHT - OFFSET, color=(255,0,0)), player=player2)
c_group.add_line(CollisionLine(screen, OFFSET, WINDOW_HEIGHT - OFFSET, OFFSET, OFFSET, color=(255,0,0)), player=player2)

brick1 = ControlledBrick(c_group, screen, 150, WINDOW_HEIGHT - 150, size_x=80, key_left=pygame.K_j, key_right=pygame.K_l)
brick2 = ControlledBrick(c_group, screen, 150, 150, size_x=80, key_left=pygame.K_a, key_right=pygame.K_d)

obj_updater = ObjectUpdater()

obj_updater.add_object(brick1)
obj_updater.add_object(brick2)
obj_updater.add_object(ball)
obj_updater.add_object(c_group)


while not DONE:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            DONE = True

    screen.fill((0, 0, 0))
    textsurface = myfont.render('Player 1: %d | Player 2: %d' % (player1.life, player2.life), False, (255, 0, 0))
    screen.blit(textsurface, (170, 20))

    obj_updater.update()
    
    pygame.display.flip()
    clock.tick(GAME_FREQUENCY)

