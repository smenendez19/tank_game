import pygame
from classes.colors import *

class Block:
    X = 0
    Y = 0
    width = 25
    height = 25
    color = RED

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.X, self.Y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.X, self.Y, self.width, self.height), 1)