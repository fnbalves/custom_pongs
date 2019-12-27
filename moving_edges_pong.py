import pygame
import time

from pong_classes import *

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500
DONE = False
GAME_FREQUENCY = 70
TEXT_X_POS = 170
INITIAL_LIFE = 5

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

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
    screen.blit(textsurface, (TEXT_X_POS, 20))
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


while not DONE:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            DONE = True

    screen.fill((0, 0, 0))
    textsurface = myfont.render('Player 1: %d | Player 2: %d' % (player1.life, player2.life), False, (255, 0, 0))
    screen.blit(textsurface, (TEXT_X_POS, 20))

    obj_updater.update()
    
    pygame.display.flip()
    clock.tick(GAME_FREQUENCY)

