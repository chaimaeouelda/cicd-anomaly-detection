import torch.nn as nn

class AutoEncoder(nn.Module):
    def __init__(self, n_features, latent=4):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_features, 8), nn.ReLU(),
            nn.Linear(8, latent), nn.ReLU())
        self.decoder = nn.Sequential(
            nn.Linear(latent, 8), nn.ReLU(),
            nn.Linear(8, n_features))

    def forward(self, x):
        return self.decoder(self.encoder(x))
