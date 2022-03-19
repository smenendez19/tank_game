import pygame
from classes.colors import *
import random

class EnemyTank:
    X = 0
    Y = 0
    speed = 5
    width = 25
    height = 25
    color = RED
    direction = "L"
    block_direction = 0

    def __init__(self, X, Y, direction):
        self.X = X
        self.Y = Y
        self.direction = direction

    def draw(self, screen):
        self.base = pygame.draw.rect(screen, self.color, (self.X, self.Y, self.width, self.height))
        if self.direction == "R":
            pygame.draw.rect(screen, GRAY, (self.X + 5, self.Y + 8, self.width + 10, self.height - 15), 0)
            pygame.draw.rect(screen, BLACK, (self.X + 5, self.Y + 8, self.width + 10, self.height - 15), 1)
        elif self.direction == "L":
            pygame.draw.rect(screen, GRAY, (self.X - 15, self.Y + 8, self.width + 10, self.height - 15), 0)
            pygame.draw.rect(screen, BLACK, (self.X - 15, self.Y + 8, self.width + 10, self.height - 15), 1)
        elif self.direction == "U":
            pygame.draw.rect(screen, GRAY, (self.X + 8, self.Y - 15, self.width - 15, self.height + 10), 0)
            pygame.draw.rect(screen, BLACK, (self.X + 8, self.Y - 15, self.width - 15, self.height + 10), 1)
        elif self.direction == "D":
            pygame.draw.rect(screen, GRAY, (self.X + 8, self.Y + 5, self.width - 15, self.height + 10), 0)
            pygame.draw.rect(screen, BLACK, (self.X + 8, self.Y + 5, self.width - 15, self.height + 10), 1)

    def move(self , direction_list):
        direction = random.choice(direction_list)
        if self.direction not in direction_list:
            self.block_direction = 0
        if self.block_direction == 0:
            if direction == "U":
                self.direction = "U"
                self.Y -= self.speed
            elif direction == "D":
                self.direction = "D"
                self.Y += self.speed
            elif direction == "L":
                self.direction = "L"
                self.X -= self.speed
            elif direction == "R":
                self.direction = "R"
                self.X += self.speed
            self.block_direction = 10
        elif self.block_direction > 0:
            if self.direction == "U":
                self.Y -= self.speed
            elif self.direction == "D":
                self.Y += self.speed
            elif self.direction == "L":
                self.X -= self.speed
            elif self.direction == "R":
                self.X += self.speed
            self.block_direction -= 1