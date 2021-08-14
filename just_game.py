import os.path
import pygame
import random
import neat
import sys


# Global Variables
screen = pygame.display.set_mode((432, 768))
bg_movement = 5
clock = pygame.time.Clock()
Obstacle_move_speed = 3

# background
bg = pygame.transform.scale(pygame.image.load('Background.png').convert(), (432, 768))

# player/ai class
class Player(pygame.sprite.Sprite):
    dude = pygame.transform.scale(pygame.image.load('TrumpFace.png').convert_alpha(), (66, 86))

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


class SpikeBall(pygame.sprite.Sprite):
    spike_ball = pygame.image.load('Spikeballs.png').convert_alpha()

    def __init__(self, y):
        self.rotateRate = 1
        self.y = y
        self.x = 216
        self.degrees = 0

        super().__init__()
        self.image = self.spike_ball
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.y -= Obstacle_move_speed
        self.rect.center = (self.x, self.y)


class Wall(pygame.sprite.Sprite):
    wall = pygame.image.load('Wall.png').convert_alpha()

    def __init__(self, y):
        self.x = random.randrange(150, 282)
        self.y = y

        # create sprite
        super().__init__()
        self.image = self.wall
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.y -= Obstacle_move_speed
        self.rect.center = (self.x, self.y)


class Laser(pygame.sprite.Sprite):
    laser_img = pygame.image.load("Laser.png").convert_alpha()

    def __init__(self, y):
        self.rotateRate = -1
        self.y = y
        self.x = 216
        self.degrees = 0
        super().__init__()
        self.image = self.rotate_laser()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.degrees += self.rotateRate
        self.y -= Obstacle_move_speed
        self.image = self.rotate_laser()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def rotate_laser(self):
        rotated_img = pygame.transform.rotate(self.laser_img, self.degrees)
        return rotated_img


def pick_obstacle(laser, spikeball, wall):
    # Putting things in the list to pick later
    obstacle_list = [laser, spikeball, wall]
    obstacle = random.choice(obstacle_list)
    return obstacle


def draw_score(points):
        color = (0, 255, 0)
        font = pygame.font.SysFont("inkfree", 50)
        text = font.render(str(int(points)), True, color)
        text_rect = text.get_rect(midright=(420, 70))
        screen.blit(text, text_rect)


# draws window
def draw_win(backg, player_sprite, obstacle_group, points):
    # drawing stuff on screen
    Backg.draw_bg(backg)
    obstacle_group.draw(screen)
    obstacle_group.update()
    player_sprite.draw(screen)
    player_sprite.update()
    draw_score(points)

    pygame.display.update()
    clock.tick(60)


def main():
    pygame.init()

    # objects
    trump = Player(216, 50)
    backg = Backg()
    laser = Laser(1000)
    spikeball = SpikeBall(1000)
    wall = Wall(1000)
    points = 0

    # Obstacle timer
    SPAWNOBSTACLE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNOBSTACLE, 3000)

    # Points timer
    ADDPOINT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDPOINT, 2000)

    # create first obstacle
    obstacle = pick_obstacle(laser, spikeball, wall)

    obstacle_group = pygame.sprite.Group()
    obstacle_group.add(obstacle)

    # adding player to sprite group
    player_sprite = pygame.sprite.Group()
    player_sprite.add(trump)

    # game starts
    while True:

        # TODO create obstacle focus function so they focus on the obstacle in front of them

        for event in pygame.event.get():
            # exit if you quit pygame
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # spawning in an obstacle
            if event.type == SPAWNOBSTACLE:
                laser = Laser(1000)
                spikeball = SpikeBall(1000)
                wall = Wall(1000)

                obstacle = pick_obstacle(laser, spikeball, wall)

                obstacle_group.add(obstacle)

            if event.type == ADDPOINT:
                points += 1

        # collisions

        # creating an empty list
        collide_list = None

        # looping through obstacles
        for o in obstacle_group:
            for trump in player_sprite:
                # seeing if they collided with obstacles
                collide_list = pygame.sprite.collide_mask(trump, o)

                # if they did then remove from lists
                if collide_list:
                    print("pain")
            # removing obstacles from the obstacle group so I save memory
            if o.y <= -100:
                obstacle_group.remove(o)

        for trump in player_sprite:
            if trump.rect.midtop[1] < 0 or trump.rect.midbottom[1] > 768 or trump.rect.midright[0] > 432 or trump.rect.midleft[0] < 0:
                print("out")

        draw_win(backg, player_sprite, obstacle_group, points)


main()


