import torch
from torch import nn
from torch import optim
import os


class LinearQNet(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear_1 = nn.Linear(in_features=input_size, out_features=hidden_size)
        self.linear_2 = nn.Linear(in_features=hidden_size, out_features=output_size)

    def forward(self, x):
        x = self.linear_1(x)
        x = nn.functional.relu(x)

        x = self.linear_2(x)

        return x

    def save(self, filename: str = 'model.pth'):
        model_folder = 'model'
        os.makedirs(model_folder, exist_ok=True)

        filename = os.path.join(model_folder, filename)
        torch.save(self.state_dict(), filename)


class QTrainer:
    def __init__(self, model: nn.Module, lr: float, gamma: float):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters())
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = state.unsqueeze(state, dim=0)
            action = action.unsqueeze(action, dim=0)
            next_state = next_state.unsqueeze(next_state, dim=0)
            reward = reward.unsqueeze(reward, dim=0)
            done = (done, )

        # 1: Predicted Q values with the current state
        pred = self.model(state)

        # 2: Q_new = reward + gamma * max(next_predicted Q value)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action).item()] = Q_new

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()