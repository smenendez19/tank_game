# Tank Game

# Imports
import pygame
import os
import sys
from levels import level_1, level_2
from classes import Tank, Block, Bullet, DestructiveBlock, EnemyTank
from classes.colors import *
import random
import yaml

# ENV VARS
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Configuration YAML
with open("config.yaml", "r") as file:
    CONFIG = yaml.load(file, Loader=yaml.FullLoader)
FPS = CONFIG["FPS"]
RESOLUTION = CONFIG["RESOLUTION"]
RESOLUTION_MAP = CONFIG["RESOLUTION_MAP"]
TITLE = CONFIG["TITLE"]

# TICKS 
TICKS_MOVE = 3
TICKS_BULLET = 25
TICKS_ENEMIES = 3

def loop():
    # Setup
    background = BLACK
    pygame.init()
    pygame.display.set_caption(TITLE)
    icon = pygame.image.load(os.path.join("sprites", "tank_icon.png"))
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode(RESOLUTION)
    clock = pygame.time.Clock()
    objects = []
    tank = None
    tank_created = False

    # Load sounds
    bullet_sound = pygame.mixer.Sound(os.path.join("sfx", "bullet.wav"))

    # Make level
    actual_level = level_1
    map_level = actual_level.MAP
    res_map = actual_level.RESOLUTION_MAP
    block_size = actual_level.BLOCK_SIZE
    for i in range(0, res_map[0] + block_size, block_size):
        for j in range(0, res_map[1] + block_size, block_size):
            # Block
            if map_level[j // block_size][i // block_size] == 2:
                objects.append(Block(i, j))
            # DestructiveBlock
            elif map_level[j // block_size][i // block_size] == 3:
                objects.append(DestructiveBlock(i, j))
            # Tanks
            elif map_level[j // block_size][i // block_size] == 1:
                if tank_created == False:
                    tank = Tank(i, j, actual_level.DIRECTION)
                    objects.append(tank)
                    tank_created = True
                else:
                    print("There are more than one tank in the level created")
                    return
            elif map_level[j // block_size][i // block_size] == 4:
                objects.append(EnemyTank(i, j, actual_level.DIRECTION))
    if tank is None:
        print("No tank setted in level")
        return

    # Ticker
    move_ticker = 0
    bullet_ticker = 0
    move_ticker_enemy = 0
    RUN_STATUS = True

    # Running
    while RUN_STATUS:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN_STATUS = False

        # Key pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if tank.Y > 0 and not collide_objects(objects, tank, "U", [Block, EnemyTank, DestructiveBlock]):
                    tank.move("U")
        if keys[pygame.K_DOWN]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if tank.Y < RESOLUTION_MAP[1] and not collide_objects(objects, tank, "D", [Block, EnemyTank, DestructiveBlock]):
                    tank.move("D")
        if keys[pygame.K_LEFT]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if tank.X > 0 and not collide_objects(objects, tank, "L", [Block, EnemyTank, DestructiveBlock]):
                    tank.move("L")
        if keys[pygame.K_RIGHT]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if tank.X < RESOLUTION_MAP[0] and not collide_objects(objects, tank, "R", [Block, EnemyTank, DestructiveBlock]):
                    tank.move("R")
        if keys[pygame.K_SPACE]:
            if bullet_ticker == 0:
                # Create bullet and move
                bullet_ticker = TICKS_BULLET
                if tank.direction == "R":
                    bullet = Bullet(tank.X + 25, tank.Y + 8, tank.direction)
                elif tank.direction == "L":
                    bullet = Bullet(tank.X - 10, tank.Y + 8, tank.direction)
                elif tank.direction == "U":
                    bullet = Bullet(tank.X + 8, tank.Y - 10, tank.direction)
                elif tank.direction == "D":
                    bullet = Bullet(tank.X + 8, tank.Y + 25, tank.direction)
                objects.append(bullet)
                # Sound of bullet
                bullet_sound.play()
        
        # Tickers
        if move_ticker > 0:
            move_ticker -= 1
        if bullet_ticker > 0:
            bullet_ticker -= 1
        if move_ticker_enemy > 0:
            move_ticker_enemy -= 1
        
        # Move objects
        move_objects(objects)

        # Move enemies
        if move_ticker_enemy == 0:
            move_ticker_enemy = TICKS_ENEMIES
            move_enemy_objects(objects)

        # Draw
        screen.fill(background)
        draw(screen, objects)

        # Remove objects out of screen
        objects = remove_objects(objects)

        # Hit Bullets
        objects = hit_bullets(objects)

        # Update
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()

# Draw objects
def draw(screen, objects):
    for object in objects:
        object.draw(screen)

# Collide objects
def collide_objects(objects, target, direction, types=[Block, DestructiveBlock]):
    for object in objects:
        if id(object) == id(target) or object.__class__ not in types:
            continue
        object_rect = pygame.Rect(object.X, object.Y, object.width, object.height)
        if direction == "U":
            target_rect_future = pygame.Rect(target.X, target.Y - target.speed, target.width, target.height)
        elif direction == "D":
            target_rect_future = pygame.Rect(target.X, target.Y + target.speed, target.width, target.height)
        elif direction == "L":
            target_rect_future = pygame.Rect(target.X - target.speed, target.Y, target.width, target.height)
        elif direction == "R":
            target_rect_future = pygame.Rect(target.X + target.speed, target.Y, target.width, target.height)
        if object_rect.colliderect(target_rect_future):
            return True
    return False

# Remove objects
def remove_objects(objects):
    for object in objects:
        if object.X < 0 or object.X > RESOLUTION[0] or object.Y < 0 or object.Y > RESOLUTION[1]:
            objects.remove(object)
    return objects

# Remove bullets
def hit_bullets(objects):
    bullets = []
    blocks = []
    destructive_blocks = []
    enemies = []
    for object in objects:
        if object.__class__ == Bullet:
            bullets.append(object)
        elif object.__class__ == Block:
            blocks.append(object)
        elif object.__class__ == DestructiveBlock:
            destructive_blocks.append(object)
        elif object.__class__ == EnemyTank:
            enemies.append(object)
    # Blocks
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet.X, bullet.Y, bullet.width, bullet.height)
        for block in blocks:
            block_rect = pygame.Rect(block.X, block.Y, block.width, block.height)
            if bullet_rect.colliderect(block_rect):
                objects.remove(bullet)
                break
    # Destructive targets
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet.X, bullet.Y, bullet.width, bullet.height)
        for destructive_block in destructive_blocks:
            destructive_block_rect = pygame.Rect(destructive_block.X, destructive_block.Y, destructive_block.width, destructive_block.height)
            if bullet_rect.colliderect(destructive_block_rect):
                objects.remove(bullet)
                objects.remove(destructive_block)
                break
    # Enemies
    for bullet in bullets:
        bullet_rect = pygame.Rect(bullet.X, bullet.Y, bullet.width, bullet.height)
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.X, enemy.Y, enemy.width, enemy.height)
            if bullet_rect.colliderect(enemy_rect):
                objects.remove(bullet)
                objects.remove(enemy)
                break
    return objects

# Move objects
def move_objects(objects):
    for object in objects:
        if isinstance(object, Bullet):
            object.move()

# Move enemy tanks
def move_enemy_objects(objects):
    enemies = []
    for object in objects:
        if isinstance(object, EnemyTank):
            enemies.append(object)
    for enemy in enemies:
        direction_list = random.sample(["U", "D", "L", "R"], 4)
        if not enemy.Y > 0 or collide_objects(objects, enemy, "U", [Block, Tank, DestructiveBlock, EnemyTank]):
            direction_list.remove("U")
        if not enemy.Y < RESOLUTION_MAP[1] or collide_objects(objects, enemy, "D", [Block, Tank, DestructiveBlock, EnemyTank]):
            direction_list.remove("D")
        if not enemy.X > 0 or collide_objects(objects, enemy, "L", [Block, Tank, DestructiveBlock, EnemyTank]):
            direction_list.remove("L")
        if not enemy.X < RESOLUTION_MAP[0] or collide_objects(objects, enemy, "R", [Block, Tank, DestructiveBlock, EnemyTank]):
            direction_list.remove("R")
        enemy.move(direction_list)
# Main
if __name__ == "__main__":
    loop()
    sys.exit()