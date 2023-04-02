import torch
from torch import nn
from torch.optim import Adam


class GRU(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 2):
        super(GRU, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers)
        self.linear = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor):
        y, _ = self.gru(x)
        return self.linear(y)

    def train(self, X, y, epochs: int, lr: float = 1e-3):
        X = torch.from_numpy(X).float()
        y = torch.from_numpy(y).float()
        loss = nn.MSELoss()
        optimizer = Adam(self.parameters(), lr=1e-3)
        for _ in range(epochs):
            y_pred = self(X)
            loss(y_pred.flatten(), y).backward()
            optimizer.step()
            optimizer.zero_grad()

    def predict(self, X):
        with torch.no_grad():
            X = torch.from_numpy(X).float()
            return self(X).detach().numpy().flatten()
