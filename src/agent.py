import torch
import random
import numpy as np
from collections import deque

from game import SnakeGameAI, Direction, Point, BLOCK_SIZE
from model import QTrainer, LinearQNet

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = LinearQNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game: SnakeGameAI):
        head = game.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y + BLOCK_SIZE)
        point_d = Point(head.x, head.y - BLOCK_SIZE)

        is_dir_l = game.direction == Direction.LEFT
        is_dir_r = game.direction == Direction.RIGHT
        is_dir_u = game.direction == Direction.UP
        is_dir_d = game.direction == Direction.DOWN

        state = [
            # Dander in front of snake
            (is_dir_r and game.is_collision(point_r)) or
            (is_dir_l and game.is_collision(point_l)) or
            (is_dir_u and game.is_collision(point_u)) or
            (is_dir_d and game.is_collision(point_d)),

            # Danger to the right
            (is_dir_u and game.is_collision(point_r)) or
            (is_dir_d and game.is_collision(point_l)) or
            (is_dir_r and game.is_collision(point_d)) or
            (is_dir_l and game.is_collision(point_u)),

            # Danger left
            (is_dir_u and game.is_collision(point_l)) or
            (is_dir_d and game.is_collision(point_r)) or
            (is_dir_r and game.is_collision(point_u)) or
            (is_dir_l and game.is_collision(point_d)),

            # Move direction
            is_dir_l,
            is_dir_r,
            is_dir_u,
            is_dir_d,

            # Food location
            game.food.x < game.head.x,  # Food to the left
            game.food.x > game.head.x,  # Food to the right
            game.food.y < game.head.y,  # Food bellow
            game.food.y > game.head.y   # Food above
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))  # Pop left if MAX_MEM reached

    def train_long_memory(self):
        mini_batch = self.memory if len(self.memory) < BATCH_SIZE else random.sample(self.memory, BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*mini_batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Random moves: tradeoff between exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()

        final_move[move] = 1
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:
        # Current state
        state_old = agent.get_state(game)

        # Get move
        final_move = agent.get_action(state_old)

        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Train short memory of the agent
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # Remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # Train long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print(f'Game: {agent.n_games} | Score: {score} | Record: {record}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)


if __name__ == '__main__':
    train()
