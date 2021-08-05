import pygame
import random
import neat
import sys


# Global Variables
screen = pygame.display.set_mode((432, 768))
bg_movement = 5
clock = pygame.time.Clock()
Obstacle_move_speed = 3

# sprites
bg = pygame.transform.scale(pygame.image.load('Background.png').convert(), (432, 768))


# player/ai class
class Player:
    dude = pygame.transform.scale(pygame.image.load('TrumpFace.png').convert_alpha(), (100, 100))

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move = 5

    def draw(self):
        dude_rect = self.dude.get_rect(center=(self.x, self.y))
        screen.blit(self.dude, dude_rect)

    def move_left(self):
        self.x -= self.move

    def move_right(self):
        self.x += self.move

    def move_down(self):
        self.y += self.move

    def move_up(self):
        self.y -= self.move

    def get_mask(self):
        return pygame.mask.from_surface(self.dude)


# Background Class
class Backg:

    def __init__(self):
        self.y = 0

    def draw_bg(self):
        if self.y <= -768:
            self.y = 0
        screen.blit(bg, (0, self.y))
        screen.blit(bg, (0, self.y + 768))
        self.y -= 5


# Obstacle class with the 3 obstacle classes inside of it
class Obstacles:

    # TODO create a random obstacle picker that makes an obstacle appear
    class SpikeBall:
        spike_ball = pygame.transform.scale(pygame.image.load('Spike ball (1).png').convert_alpha(), (90, 90))

        def __init__(self):
            # spike balls
            self.rotateRate = 3
            self.distance = 200
            self.y = 800
            self.x = random.randrange(75, 200)
            self.degrees = 0
            self.x2 = self.x + self.distance

        def draw_spike_ball(self):
            rotated_img = pygame.transform.rotate(self.spike_ball, self.degrees)
            spike_rect = rotated_img.get_rect(center=(self.x, self.y))
            spike_rect2 = rotated_img.get_rect(center=(self.x2, self.y))
            screen.blit(rotated_img, spike_rect)
            screen.blit(rotated_img, spike_rect2)
            self.y -= Obstacle_move_speed
            self.degrees += self.rotateRate

        def get_mask(self):
            return pygame.mask.from_surface(self.spike_ball)

        def collision(self, player):
            spikeball_mask = self.get_mask()
            dude_mask = player.get_mask()

            offset = (self.x - round(player.x), round(self.y) - round(player.y))
            offset2 = (self.x2 - round(player.x), round(self.y) - round(player.y))
            result = spikeball_mask.overlap(dude_mask, offset)
            result2 = spikeball_mask.overlap(dude_mask, offset2)

            if result or result2:
                return True
            else:
                return False

    class Wall:
        left_wall = pygame.image.load('Wall.png').convert_alpha()
        right_wall = pygame.transform.flip(left_wall, True, False)

        def __init__(self):
            self.gap = 150
            self.y = 1500
            self.x = random.randrange(70, 263)
            self.rightx = self.x + self.gap

        def draw_wall(self):
            # left wall
            left_wall_rect = self.left_wall.get_rect(midright=(self.x, self.y))
            # right wall
            right_wall_rect = self.right_wall.get_rect(midleft=(self.rightx, self.y))
            # put wall on screen
            screen.blit(self.left_wall, left_wall_rect)
            screen.blit(self.right_wall, right_wall_rect)
            self.y -= Obstacle_move_speed

        def collision(self, player):

            # TODO fix the collision saying true even though I am not hitting it
            # getting masks
            dude_mask = player.get_mask()
            left_wall_mask = pygame.mask.from_surface(self.left_wall)
            right_wall_mask = pygame.mask.from_surface(self.right_wall)

            # finding the overlap
            offset_left = (self.x - round(player.x), round(self.y) - round(player.y))
            offset_right = (self.rightx - round(player.x), round(self.y) - round(player.y))

            # checking for collision
            result_left = left_wall_mask.overlap(dude_mask, offset_left)
            result_right = right_wall_mask.overlap(dude_mask, offset_right)

            if result_left or result_right:
                return True
            else:
                return False


# draws window
def draw_win(backg, player, wall, spikeball):
    # drawing stuff on screen
    Backg.draw_bg(backg)
    Player.draw(player)
    Obstacles.SpikeBall.draw_spike_ball(spikeball)
    Obstacles.Wall.draw_wall(wall)

    pygame.display.update()
    clock.tick(60)


def run():
    pygame.init()

    # pre game start
    me = Player(216, 50)
    backg = Backg()
    spikeball = Obstacles.SpikeBall()
    wall = Obstacles.Wall()

    # moving left and right for testing
    move_right = False
    move_left = False

    # game starts
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # inputs for testing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    move_left = True
                if event.key == pygame.K_d:
                    move_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_d:
                    move_right = False

        # true of false for testing purposes
        if move_right:
            me.move_right()
        if move_left:
            me.move_left()
        else:
            pass

        if Obstacles.Wall.collision(wall, me):
            print("PAIN!")
        if Obstacles.SpikeBall.collision(spikeball, me):
            print("PAIN!")
        else:
            pass
        draw_win(backg, me, wall, spikeball)


run()
