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
class Player(pygame.sprite.Sprite):
    dude = pygame.transform.scale(pygame.image.load('TrumpFace.png').convert_alpha(), (100, 100))

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.move = 5
        self.image = self.dude
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

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


# TODO create a random obstacle picker that makes an obstacle appear
class SpikeBall:
    spike_ball = pygame.transform.scale(pygame.image.load('Spike ball (1).png').convert_alpha(), (90, 90))

    def __init__(self, y):
        self.rotateRate = 3
        self.distance = 200
        self.y = y
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

    def __init__(self, y):
        self.midx = 212
        self.midy = 28
        self.gap = 150 + self.midx + self.midx
        self.y = y - self.midy
        self.x = random.randrange(70, 263) - self.midx
        self.rightx = self.x + self.gap
        self.correction_x = 165
        self.correction_y = 23

    def draw_wall(self):
        # left wall
        left_wall_rect = self.left_wall.get_rect(center=(self.x, self.y))
        # right wall
        right_wall_rect = self.right_wall.get_rect(center=(self.rightx, self.y))
        # put wall on screen
        screen.blit(self.left_wall, left_wall_rect)
        screen.blit(self.right_wall, right_wall_rect)
        self.y -= Obstacle_move_speed

    def get_mask_left(self):
        return pygame.mask.from_surface(self.left_wall)

    def get_mask_right(self):
        return pygame.mask.from_surface(self.right_wall)

    def collision(self, player):

        # getting masks
        dude_mask = player.get_mask()
        wall_mask = self.get_mask_left()

        # finding the overlap
        offset_left = (self.x - round(player.x) + self.correction_x, round(self.y) - round(player.y)-self.correction_y)
        offset_right = (self.rightx - round(player.x) + self.correction_x, round(self.y) - round(player.y)-self.correction_y)

        # checking for collision
        result_left = wall_mask.overlap(dude_mask, offset_left)
        result_right = wall_mask.overlap(dude_mask, offset_right)

        if result_left or result_right:
            return True
        else:
            return False


class Laser(pygame.sprite.Sprite):
    # TODO make this a sprite class thing, need to learn about them
    laser_img = pygame.image.load("Laser.png").convert_alpha()

    def __init__(self, y):
        self.rotateRate = -1
        self.y = y
        self.x = 216
        self.degrees = 0
        # self.correction_x = 230
        # self.correction_y = 220
        super().__init__()
        self.image = self.rotate_laser()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.degrees += self.rotateRate
        # self.y -= Obstacle_move_speed
        self.image = self.rotate_laser()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def rotate_laser(self):
        rotated_img = pygame.transform.rotate(self.laser_img, self.degrees)
        return rotated_img


# draws window
def draw_win(backg, player_sprite, obstacle_group):
    # drawing stuff on screen
    Backg.draw_bg(backg)
    obstacle_group.draw(screen)
    obstacle_group.update()
    player_sprite.draw(screen)
    player_sprite.update()
    # Wall.draw_wall(wall)
    # SpikeBall.draw_spike_ball(spikeball)

    pygame.display.update()
    clock.tick(60)


def run():
    pygame.init()

    # declaring sprites
    trump = Player(216, 50)
    backg = Backg()
    laser = Laser(500)
    # spikeball = SpikeBall(900)
    # wall = Wall(1200)

    obstacle_group = pygame.sprite.Group()
    obstacle_group.add(laser)

    player_sprite = pygame.sprite.Group()
    player_sprite.add(trump)

    # game starts
    while True:

        for event in pygame.event.get():
            # exit if you quit pygame
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_win(backg, player_sprite, obstacle_group)

        # collisions
        collide_list = None
        for o in obstacle_group:
            collide_list = pygame.sprite.collide_mask(trump, o)

        if collide_list:
            print("PAIN")


run()
