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


class SnakeGame:
    def __init__(self, w: int = 640, h: int = 480, initial_speed: float = 12.0):
        self.w = w
        self.h = h
        self.speed = initial_speed

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
            self.speed += 0.05 * self.speed
            self._place_food()
        else:
            self.snake.pop()  # If snake did not eat food remove last point

        # Update UI and clock
        self._update_ui()
        self.clock.tick(self.speed)

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


class SnakeGameAI(SnakeGame):
    def __init__(self, w: int = 640, h: int = 480, initial_speed: float = 12):
        super().__init__(w, h, initial_speed)
        self.frame_iteration = 0

    def reset(self):
        self.__init__(self.w, self.h, self.speed)

    def play_step(self, action):
        self.frame_iteration += 1
        # Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Move snake (append new head in the correct direction
        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        # Check for game over
        game_over = False
        if self._is_collision() or self.frame_iteration > 100 * len(self.snake):
            reward = -10
            game_over = True
            return reward, game_over, self.score

        # Place new food or just move
        if self.head == self.food:
            reward = 10
            self.score += 1
            self.speed += 0.05 * self.speed
            self._place_food()
        else:
            self.snake.pop()  # If snake did not eat food remove last point

        # Update UI and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # Return game over and clock
        return reward, game_over, self.score

    def _move(self, action):
        # [straight, right turn, left turn]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        new_direction = self.direction
        if action[0]:
            new_direction = clock_wise[idx]  # No change
        elif action[1]:
            new_direction = clock_wise[(idx + 1) % len(clock_wise)]  # Clock wise rotation
        elif action[2]:
            new_direction = clock_wise[(idx - 1) % len(clock_wise)]  # Anti clock wise rotation

        self.direction = new_direction

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

    def _is_collision(self, pt: Point | None = None):
        if pt is None:
            pt = self.head

        # Collision with boundaries
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Collision with self
        if pt in self.snake[1:]:
            return True

        return False


if __name__ == '__main__':
    game = SnakeGameAI(1280, 720)
    actions = [
        [1, 0, 0],  # No direction change
        [0, 1, 0],  # Right turn
        [0, 0, 1]   # Left turn
    ]

    while True:
        action_idx = random.randint(0, len(actions) - 1)
        reward, game_over, score = game.play_step(actions[action_idx])

        if game_over:
            break

    print(f'Final score {score}')
    pygame.quit()
