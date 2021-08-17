import os.path
import pygame
import random
import neat
import sys


# Global Variables
screen = pygame.display.set_mode((432, 768))
# background movement
bg_movement = 5
# creating clock

# Obstacle Y move speed
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
        self.rect

    def move_left(self):
        self.x -= self.move
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move_right(self):
        self.x += self.move
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move_down(self):
        self.y += self.move
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move_up(self):
        self.y -= self.move
        self.rect = self.image.get_rect(center=(self.x, self.y))

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
def draw_win(backg, players, obstacles, points):
    # drawing stuff on screen
    Backg.draw_bg(backg)
    for o in obstacles:
        screen.blit(o.image, o.rect)
        o.update()
    for p in players:
        screen.blit(p.image, p.rect)
    draw_score(points)
    pygame.display.update()


def main(genomes, config):
    pygame.init()
    # NEAT lists
    nets = []
    ge = []
    trumps = []

    # creating the trumps in the genome
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        trumps.append(Player(216, 100))
        g.fitness = 0
        ge.append(g)

    # game variables
    backg = Backg()
    laser = Laser(1000)
    spikeball = SpikeBall(1000)
    wall = Wall(1000)
    points = 0
    clock = pygame.time.Clock()

    # Obstacle timer
    SPAWNOBSTACLE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNOBSTACLE, 3000)

    # Points timer
    ADDPOINT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDPOINT, 2000)

    # creating first obstacle
    obstacles = []
    obstacle = pick_obstacle(laser, spikeball, wall)
    obstacles.append(obstacle)

    # game starts
    run = True
    while run:
        # giving reward if they make it pass an obstacle, checking for amount of trumps
        obstacle_ind = 0
        if len(trumps) > 0:
            if len(obstacles) > 1 and trumps[0].y > obstacles[0].rect.midbottom[1]:
                obstacle_ind = 1
        else:
            run = False
            obstacles.clear()
            pygame.time.set_timer(SPAWNOBSTACLE, 0)
            pygame.time.set_timer(ADDPOINT, 0)
            break

        # give fitness for surviving
        for x, trump in enumerate(trumps):
            ge[x].fitness += 0.1

            # creating output nodes
            center_y = abs(trump.y - obstacles[obstacle_ind].y)
            center_x = abs(trump.x - obstacles[obstacle_ind].x)
            top_y = abs(trump.y - obstacles[obstacle_ind].rect.midtop[1])
            top_x = abs(trump.x - obstacles[obstacle_ind].rect.midtop[0])
            difference_y = abs(obstacles[obstacle_ind].rect.midtop[1] - obstacles[obstacle_ind].y)

            # making output node list
            output = nets[x].activate((trump.x, trump.y, center_y, center_x, top_y, top_x, difference_y))

            # checking each node for a value
            if output[0] > 0.5:
                trump.move_down()
            if output[1] > 0.5:
                trump.move_up()
            if output[2] > 0.5:
                trump.move_left()
            if output[3] > 0.5:
                trump.move_right()

        # checking events that happen
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
                obstacles.append(obstacle)

            # adding a point
            if event.type == ADDPOINT:
                points += 1

                # giving fitness to trumps for getting a better score
                for g in ge:
                    g.fitness += 5

        # collisions

        # creating an empty list
        collide_list = None

        # looping through obstacles
        for o in obstacles:
            for x, trump in enumerate(trumps):
                # seeing if they collided with obstacles
                collide_list = pygame.sprite.collide_mask(trump, o)

                # if they did then remove from lists
                if collide_list:
                    ge[x].fitness -= 3
                    trumps.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            # removing obstacles from the obstacle group so I save memory
            if o.y <= -100:
                obstacles.remove(o)

        for x, trump in enumerate(trumps):
            if trump.rect.midtop[1] < 0 or trump.rect.midbottom[1] > 768 or trump.rect.midright[0] > 432 or trump.rect.midleft[0] < 0:
                ge[x].fitness -= 3
                trumps.pop(x)
                nets.pop(x)
                ge.pop(x)

        clock.tick(60)
        draw_win(backg, trumps, obstacles, points)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 1000)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)
