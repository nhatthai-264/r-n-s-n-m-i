import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 40
CELL_NUMBER = 20
SCREEN_WIDTH = CELL_SIZE * CELL_NUMBER
SCREEN_HEIGHT = CELL_SIZE * CELL_NUMBER

FPS = 60

# Colors
BG_COLOR = (175, 215, 70)
GRID_COLOR = (167, 209, 61)

# Paths
SPRITES_DIR = "sprites"

def load_sprite(filename):
    path = os.path.join(SPRITES_DIR, filename)
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
    else:
        print(f"Lỗi: Không tìm thấy sprite '{filename}'. Sẽ dùng khối màu đỏ thay thế.")
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surf.fill((255, 0, 0))
        return surf

class SNAKE:
    def __init__(self):
        self.body = [pygame.math.Vector2(5, 10), pygame.math.Vector2(4, 10), pygame.math.Vector2(3, 10)]
        self.direction = pygame.math.Vector2(1, 0)
        self.new_block = False

        # Load Sprites
        self.head_up = load_sprite('head_up.png')
        self.head_down = load_sprite('head_down.png')
        self.head_right = load_sprite('head_right.png')
        self.head_left = load_sprite('head_left.png')
        
        self.tail_up = load_sprite('tail_up.png')
        self.tail_down = load_sprite('tail_down.png')
        self.tail_right = load_sprite('tail_right.png')
        self.tail_left = load_sprite('tail_left.png')
        
        self.body_img = load_sprite('body.png')

    def draw_snake(self, screen):
        self.update_head_graphics()
        self.update_tail_graphics()

        for index, block in enumerate(self.body):
            x = int(block.x * CELL_SIZE)
            y = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body) - 1:
                screen.blit(self.tail, block_rect)
            else:
                screen.blit(self.body_img, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == pygame.math.Vector2(1, 0): self.head = self.head_left
        elif head_relation == pygame.math.Vector2(-1, 0): self.head = self.head_right
        elif head_relation == pygame.math.Vector2(0, 1): self.head = self.head_up
        elif head_relation == pygame.math.Vector2(0, -1): self.head = self.head_down

    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == pygame.math.Vector2(1, 0): self.tail = self.tail_left
        elif tail_relation == pygame.math.Vector2(-1, 0): self.tail = self.tail_right
        elif tail_relation == pygame.math.Vector2(0, 1): self.tail = self.tail_up
        elif tail_relation == pygame.math.Vector2(0, -1): self.tail = self.tail_down

    def move_snake(self):
        if self.new_block == True:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]

    def add_block(self):
        self.new_block = True

    def reset(self):
        self.body = [pygame.math.Vector2(5, 10), pygame.math.Vector2(4, 10), pygame.math.Vector2(3, 10)]
        self.direction = pygame.math.Vector2(1, 0)


class FOOD:
    def __init__(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = pygame.math.Vector2(self.x, self.y)
        self.food_img = load_sprite('food.png')

    def draw_food(self, screen):
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        screen.blit(self.food_img, food_rect)
        
    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = pygame.math.Vector2(self.x, self.y)


class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.food = FOOD()

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def draw_elements(self, screen):
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)

    def check_collision(self):
        if self.food.pos == self.snake.body[0]:
            self.food.randomize()
            self.snake.add_block()
            
            # Không cho phép mồi sinh ra đè lên mình rắn
            while self.food.pos in self.snake.body:
                self.food.randomize()

    def check_fail(self):
        # Đâm vào tường
        if not 0 <= self.snake.body[0].x < CELL_NUMBER or not 0 <= self.snake.body[0].y < CELL_NUMBER:
            self.game_over()

        # Đâm vào chính mình
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def game_over(self):
        self.snake.reset()

def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rắn săn mồi (Snake Game)")
    clock = pygame.time.Clock()

    game = MAIN()

    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, 150) # Tốc độ chạy của rắn (ms)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == SCREEN_UPDATE:
                game.update()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.snake.direction.y != 1:
                    game.snake.direction = pygame.math.Vector2(0, -1)
                elif event.key == pygame.K_DOWN and game.snake.direction.y != -1:
                    game.snake.direction = pygame.math.Vector2(0, 1)
                elif event.key == pygame.K_LEFT and game.snake.direction.x != 1:
                    game.snake.direction = pygame.math.Vector2(-1, 0)
                elif event.key == pygame.K_RIGHT and game.snake.direction.x != -1:
                    game.snake.direction = pygame.math.Vector2(1, 0)

        if not running:
            break

        screen.fill(BG_COLOR)
        draw_grid(screen)
        game.draw_elements(screen)
        
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
