import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('arial', 25)
# font = pygame.font.Font('arial.ttf', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 12


class SnakeGame:
    def __init__(self, w: int = 640, h: int = 480):
        self.w = w
        self.h = h

        # Init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')

        self.clock = pygame.time.Clock()

        # Init game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w//2, self.h//2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - 2*BLOCK_SIZE, self.head.y)
                      ]
        self.score = 0
        self.food = None
        self._place_food()

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE  # Align to the starting coordinates of a block
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        # Check if new Food point is not under the snake
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        global SPEED
        # Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not self._is_opposite_direction(Direction.LEFT):
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and not self._is_opposite_direction(Direction.RIGHT):
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and not self._is_opposite_direction(Direction.UP):
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and not self._is_opposite_direction(Direction.DOWN):
                    self.direction = Direction.DOWN

        # Move snake (append new head in the correct direction
        self._move()
        self.snake.insert(0, self.head)

        # Check for game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # Place new food or just move
        if self.head == self.food:
            self.score += 1
            SPEED += 0.05 * SPEED
            self._place_food()
        else:
            self.snake.pop()  # If snake did not eat food remove last point

        # Update UI and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # Return game over and clock
        return game_over, self.score

    def _is_collision(self):
        # Collision with boundaries
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # Collision with self
        if self.head in self.snake[1:]:
            return True

        return False

    def _move(self):
        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        if self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        if self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        if self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8))

        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render(f'Score: {self.score}', True, WHITE)
        self.display.blit(text, [0, 0])

        pygame.display.flip()

    def _is_opposite_direction(self, new_dir: Direction):
        if self.direction == Direction.RIGHT and new_dir == Direction.LEFT:
            return True
        elif self.direction == Direction.LEFT and new_dir == Direction.RIGHT:
            return True
        elif self.direction == Direction.UP and new_dir == Direction.DOWN:
            return True
        elif self.direction == Direction.DOWN and new_dir == Direction.UP:
            return True
        else:
            return False


if __name__ == '__main__':
    game = SnakeGame(1280, 720)

    while True:
        game_over, score = game.play_step()

        if game_over:
            break

    print(f'Final score {score}')

    pygame.quit()
