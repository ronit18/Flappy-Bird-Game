# Flappy_bird Game
# Made By RonitGandhi


# modules
import random
from math import dist, copysign
import pygame
from pygame.locals import *

pygame.init()  # initialiazes the Pygame window.

# width and height of pygame window
WIDTH, HEIGHT = 1000, 1010
display = pygame.display.set_mode((WIDTH, HEIGHT))

# for score
font = pygame.font.SysFont(None, 100)

# sounds of score and hit and jump
score_sound = pygame.mixer.Sound(
    './Sounds/score.mp3')
score_sound.set_volume(0.3)
punch_sound = pygame.mixer.Sound(
    './Sounds/punch.mp3')
punch_sound.set_volume(0.1)
jump_sound = pygame.mixer.Sound(
    './Sounds/jump.mp3')
jump_sound.set_volume(0.3)

# Games fps
FPS = 60
clock = pygame.time.Clock()

# Colours
BLUE = (30, 144, 255)
WHITE = (255, 255, 255)

# for birds motion
PIPE_GAP = 300
GRAVITY = 0.6
JUMP_VELOCITY = 15


class EdgesMixin:

    @property
    def x(self):
        return self.rect[0]

    @property
    def y(self):
        return self.rect[1]

    @property
    def w(self):
        return self.rect[2]

    @property
    def h(self):
        return self.rect[3]


# Class for Bird
class BirdSprite(EdgesMixin, pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # loades image of bird from the images folder
        self.image = pygame.image.load('./Images/bird.png')
        self.image.set_colorkey(WHITE)
        # we use this to remove alpha backgroud from image.
        self.image.convert_alpha()

        self.bird_image = pygame.image.load('./Images/bird.png')
        self.bird_image.set_colorkey(WHITE)
        self.bird_image.convert_alpha()

        self.rect = self.image.get_rect()
        # position of bird on the game window
        self.rect.center = (100, HEIGHT // 2)

        self.velocity = 0
        self.degree = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)  # draw/update of bird on display

    def collide(self, pipe: 'Pipe'):
        return (
            pygame.sprite.collide_mask(self, pipe.top) or
            pygame.sprite.collide_mask(self, pipe.bot)
        )


# Class for Pipes
class PipeSprite(EdgesMixin, pygame.sprite.Sprite):
    def __init__(self, side: str, padding: int, from_right: int = 0):
        super().__init__()
        # loades image of pipe from the images folder #here f string is used so that after wards we can use and if-else statement to decide whether top or bottom of pipe we have to use.
        self.image = pygame.image.load(f'./Images/{side}_pipe.png')
        self.image.set_colorkey(WHITE)
        # we use this to remove alpha backgroud from image.
        self.image.convert_alpha()

        self.rect = self.image.get_rect()

        width = WIDTH + self.w // 2 - from_right  # width of pipe on game window

        # height of pipe on game window
        # using if-else statement for top or bottom pipe of height.
        if side == 'top':
            height = -padding + self.h // 2 - PIPE_GAP
        else:
            height = HEIGHT - padding - self.h // 2 + PIPE_GAP

        # position of pipes on the game window.
        self.rect.center = (width, height)

    def draw(self, surface):  # draw/update of pipes on display
        surface.blit(self.image, self.rect)


class Pipe:
    def __init__(self, top_pipe, bottom_pipe, y_delta=0):
        self.top = top_pipe
        self.bot = bottom_pipe
        self.y_delta = y_delta


def create_pipe(from_right=0):
    padding = random.randint(-100, 100)
    top_pipe = PipeSprite('top', padding, from_right)
    bottom_pipe = PipeSprite('bottom', padding, from_right)

    y_delta = 0 if score <= 3 else random.randint(2, 4)
    y_delta = random.choice([y_delta, -y_delta])

    return Pipe(top_pipe, bottom_pipe, y_delta)


# using the declared classes
score = 0
bird = BirdSprite()
pipes = [create_pipe(400)]
pipe_to_right = pipes[0]

# games starting condition
game_on = False
init = True
jump_freeze = False

# Game loop
while True:
    pressed = pygame.key.get_pressed()

    if game_on or init:
        display.fill(BLUE)  # filling the main window colour

        if pipe_to_right.top.x < bird.x:
            score_sound.play()
            score += 1
            pipe_to_right = pipes[1]

        if pipes[0].top.x + pipes[0].top.w < 0:
            pipes.pop(0)

        if pipes[-1].top.x == 400:
            pipes.append(create_pipe())

        for pipe in pipes:
            if (
                pipe.top.y + pipe.top.h < 100 or
                pipe.bot.y > HEIGHT - 100
            ):
                pipe.y_delta *= -1
            pipe.top.rect.move_ip(-5, pipe.y_delta)
            pipe.bot.rect.move_ip(-5, pipe.y_delta)
            pipe.top.draw(display)
            pipe.bot.draw(display)

        if not init:
            if pressed[K_SPACE] and not jump_freeze:
                jump_sound.play()
                bird.velocity = JUMP_VELOCITY
                jump_freeze = True
            bird.velocity -= GRAVITY
            prev_y = bird.y
            bird.rect.move_ip(0, -bird.velocity)

            y_diff = prev_y - bird.y
            rot = (
                (max(min(y_diff, JUMP_VELOCITY), -JUMP_VELOCITY) + JUMP_VELOCITY) /
                (JUMP_VELOCITY * 2)
            )
            new_degree = 160 * rot - 70
            degree_diff = dist((bird.degree, ), (new_degree, ))
            new_degree = bird.degree + copysign(
                min(40, abs(degree_diff)),
                new_degree - bird.degree,
            )
            bird.image = pygame.transform.rotate(bird.bird_image, new_degree)
            bird.degree = new_degree

            if (
                bird.y <= 0 or bird.y >= HEIGHT - bird.h or
                bird.collide(pipes[0])
            ):
                punch_sound.play()
                game_on = False
        # drawing on game window
        bird.draw(display)  # bird draw

        image = font.render(str(score), True, WHITE)

        display.blit(image, (20, 20))

    if pressed[K_SPACE] and not game_on:  # SpaceBar to jump the bird
        game_on = True
        score = 0
        bird = BirdSprite()

        if len(pipes) != 1:
            pipes = [create_pipe(400)]
            pipe_to_right = pipes[0]

    for event in pygame.event.get():  # for quiting the game loop
        if event.type == QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN and event.key == K_SPACE:
            jump_freeze = False

    pygame.display.update()  # updates the display and initiliazes the the PyGame window
    clock.tick(FPS)

    init = False
