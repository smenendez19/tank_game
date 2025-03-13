# Tank Game

# Imports
import os
import random
import sys

import pygame
import yaml

from classes import Block, Bullet, DestructiveBlock, EnemyTank, Tank
from classes.colors import BLACK, RED, WHITE
from levels import level_1, level_2

# ENV VARS
os.environ["SDL_VIDEO_CENTERED"] = "1"

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


# Loop application
def loop():
    # Setup menu
    pygame.init()
    pygame.display.set_caption(TITLE)
    icon = pygame.image.load(os.path.join("sprites", "tank_icon.png"))
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode(RESOLUTION)
    clock = pygame.time.Clock()

    while True:
        ### MENU ###
        level = menu(screen, clock)
        ### GAME ###
        status = loop_level(screen, clock, level)
        if status == "GAME_OVER":
            go_status = game_over(screen, clock)
            if go_status == "EXIT":
                break
        elif status == "EXIT":
            break
        elif status == "COMPLETED":
            continue


# Menu
def menu(screen, clock):
    return level_1


def game_over(screen, clock):
    # Final status: MENU, RESTART, EXIT
    FINAL_STATUS = "MENU"
    GAME_OVER_STATUS = True
    background = BLACK
    font = pygame.font.SysFont(None, 24)

    while GAME_OVER_STATUS:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_OVER_STATUS = False
                FINAL_STATUS = "EXIT"
        # Click
        # TODO : Add click function for these objects
        mouseClick = pygame.mouse.get_pressed()
        if sum(mouseClick) > 0:
            posX, posY = pygame.mouse.get_pos()
            if posX >= 350 and posX <= 350 + 135 and posY >= 435 and posY <= 435 + 50:
                FINAL_STATUS = "RESTART"
                GAME_OVER_STATUS = False
            if posX >= 10 and posX <= 10 + 155 and posY >= 435 and posY <= 435 + 50:
                FINAL_STATUS = "MENU"
                GAME_OVER_STATUS = False
        # Draw
        screen.fill(background)
        # Texts
        font = pygame.font.SysFont(None, 26)
        text_game_over = font.render("GAME OVER", True, WHITE)
        screen.blit(text_game_over, (210, 250))
        pygame.draw.rect(screen, RED, (350, 435, 135, 50), 2)
        text_restart = font.render("RESTART LEVEL", True, WHITE)
        screen.blit(text_restart, (350, 450))
        pygame.draw.rect(screen, RED, (10, 435, 155, 50), 2)
        text_menu = font.render("RETURN TO MENU", True, WHITE)
        screen.blit(text_menu, (10, 450))
        # Update
        pygame.display.update()
        clock.tick(FPS)
    print(FINAL_STATUS)
    return FINAL_STATUS


# Loop level
def loop_level(screen, clock, level):
    ### LEVEL-FUNCTIONS ###
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
        player_tank = []
        for object in objects:
            if object.__class__ == Bullet:
                bullets.append(object)
            elif object.__class__ == Block:
                blocks.append(object)
            elif object.__class__ == DestructiveBlock:
                destructive_blocks.append(object)
            elif object.__class__ == EnemyTank:
                enemies.append(object)
            elif object.__class__ == Tank:
                player_tank.append(object)
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
        # Tank
        for bullet in bullets:
            bullet_rect = pygame.Rect(bullet.X, bullet.Y, bullet.width, bullet.height)
            for tank in player_tank:
                tank_rect = pygame.Rect(tank.X, tank.Y, tank.width, tank.height)
                if bullet_rect.colliderect(tank_rect):
                    objects.remove(bullet)
                    tank.hit()
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

    # Get objects
    def get_objects(objects, type):
        objects_list = []
        for object in objects:
            if object.__class__ == type:
                objects_list.append(object)
        return objects_list

    background = BLACK
    GAME_STATUS = True
    # Final status: COMPLETED, IN_GAME, GAME_OVER, EXIT
    FINAL_STATUS = "IN_GAME"

    ### PRE-GAME ###
    # Ticker
    move_ticker = 0
    bullet_ticker = 0
    move_ticker_enemy = 0
    # Level objects
    objects = []
    player_tank = None
    # Load sounds
    bullet_sound = pygame.mixer.Sound(os.path.join("sfx", "bullet.wav"))
    # Make level
    tank_created = False
    actual_level = level
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
                    player_tank = Tank(i, j, actual_level.DIRECTION)
                    objects.append(player_tank)
                    tank_created = True
                else:
                    raise Exception("Only one tank is allowed")
            elif map_level[j // block_size][i // block_size] == 4:
                objects.append(EnemyTank(i, j, actual_level.DIRECTION))
    if player_tank is None:
        raise Exception("No tank created in level")
    ### GAME ###
    while GAME_STATUS:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_STATUS = False
                FINAL_STATUS = "EXIT"

        if player_tank.destroyed:
            GAME_STATUS = False
            FINAL_STATUS = "GAME_OVER"

        # Key pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if player_tank.Y > 0 and not collide_objects(objects, player_tank, "U", [Block, EnemyTank, DestructiveBlock]):
                    player_tank.move("U")
        if keys[pygame.K_DOWN]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if player_tank.Y < RESOLUTION_MAP[1] and not collide_objects(objects, player_tank, "D", [Block, EnemyTank, DestructiveBlock]):
                    player_tank.move("D")
        if keys[pygame.K_LEFT]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if player_tank.X > 0 and not collide_objects(objects, player_tank, "L", [Block, EnemyTank, DestructiveBlock]):
                    player_tank.move("L")
        if keys[pygame.K_RIGHT]:
            if move_ticker == 0:
                move_ticker = TICKS_MOVE
                # Collide
                if player_tank.X < RESOLUTION_MAP[0] and not collide_objects(objects, player_tank, "R", [Block, EnemyTank, DestructiveBlock]):
                    player_tank.move("R")
        if keys[pygame.K_SPACE]:
            if bullet_ticker == 0:
                # Create bullet and move
                bullet_ticker = TICKS_BULLET
                if player_tank.direction == "R":
                    bullet = Bullet(player_tank.X + 25, player_tank.Y + 8, player_tank.direction)
                elif player_tank.direction == "L":
                    bullet = Bullet(player_tank.X - 10, player_tank.Y + 8, player_tank.direction)
                elif player_tank.direction == "U":
                    bullet = Bullet(player_tank.X + 8, player_tank.Y - 10, player_tank.direction)
                elif player_tank.direction == "D":
                    bullet = Bullet(player_tank.X + 8, player_tank.Y + 25, player_tank.direction)
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

        # Enemy bullets
        enemy_tanks = get_objects(objects, EnemyTank)
        for tank in enemy_tanks:
            if tank.fire_bullet() == True:
                if tank.direction == "R":
                    bullet = Bullet(tank.X + 25, tank.Y + 8, tank.direction)
                elif tank.direction == "L":
                    bullet = Bullet(tank.X - 10, tank.Y + 8, tank.direction)
                elif tank.direction == "U":
                    bullet = Bullet(tank.X + 8, tank.Y - 10, tank.direction)
                elif tank.direction == "D":
                    bullet = Bullet(tank.X + 8, tank.Y + 25, tank.direction)
                objects.append(bullet)

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
    return FINAL_STATUS


# Main
if __name__ == "__main__":
    loop()
    sys.exit()
