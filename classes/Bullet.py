import pygame
from classes.colors import *

class Bullet:
    X = 0
    Y = 0
    width = 10
    height = 10
    speed = 10
    color = WHITE
    direction = "L"

    def __init__(self, X, Y, direction):
        self.X = X
        self.Y = Y
        self.direction = direction

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.X, self.Y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.X, self.Y, self.width, self.height), 1)

    def move(self):
        if self.direction == "U":
            self.Y -= self.speed
        elif self.direction == "D":
            self.Y += self.speed
        elif self.direction == "L":
            self.X -= self.speed
        elif self.direction == "R":
            self.X += self.speed
        else:
            print("Invalid direction")