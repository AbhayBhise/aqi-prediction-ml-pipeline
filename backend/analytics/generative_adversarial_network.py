import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Generator Model (Unit VI)
class AQIGenerator(nn.Module):
    def __init__(self, latent_dim, output_dim):
        super(AQIGenerator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim),
            nn.Tanh() # Output normalized data
        )
        
    def forward(self, z):
        return self.model(z)

# Discriminator Model (Unit VI)
class AQIDiscriminator(nn.Module):
    def __init__(self, input_dim):
        super(AQIDiscriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid() # Probability of being REAL
        )
        
    def forward(self, x):
        return self.model(x)

def train_gan_demo():
    print("[GAN] Initializing Generative Adversarial Network...")
    
    latent_dim = 10
    data_dim = 24 # Simulating a 24-hour AQI trend
    
    generator = AQIGenerator(latent_dim, data_dim)
    discriminator = AQIDiscriminator(data_dim)
    
    # Loss and Optimizers (Unit VI: Problems with BCE Loss)
    criterion = nn.BCELoss()
    optimizer_g = optim.Adam(generator.parameters(), lr=0.0002)
    optimizer_d = optim.Adam(discriminator.parameters(), lr=0.0002)
    
    print("\n[GAN] Starting Adversarial Training...")
    print("Goal: Generator learns to create realistic AQI patterns, Discriminator learns to spot 'fakes'.")
    
    for epoch in range(1, 6):
        # 1. Train Discriminator
        real_data = torch.randn(16, data_dim) # Real samples
        fake_data = generator(torch.randn(16, latent_dim)) # Generated samples
        
        d_loss_real = criterion(discriminator(real_data), torch.ones(16, 1))
        d_loss_fake = criterion(discriminator(fake_data.detach()), torch.zeros(16, 1))
        d_loss = d_loss_real + d_loss_fake
        
        optimizer_d.zero_grad()
        d_loss.backward()
        optimizer_d.step()
        
        # 2. Train Generator (Unit VI: Mode Collapse / Gradient issues)
        g_loss = criterion(discriminator(fake_data), torch.ones(16, 1))
        
        optimizer_g.zero_grad()
        g_loss.backward()
        optimizer_g.step()
        
        print(f"Epoch {epoch}/5 - D_Loss: {d_loss.item():.4f}, G_Loss: {g_loss.item():.4f}")
        
    print("\n[GAN] Demo complete. This implementation covers Generator, Discriminator, and BCE Loss (Unit VI).")

if __name__ == "__main__":
    train_gan_demo()
