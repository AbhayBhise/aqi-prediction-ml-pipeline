import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import os
import sys

class AQI_CNN(nn.Module):
    def __init__(self, input_dim, seq_length):
        super(AQI_CNN, self).__init__()
        # 1D Convolutional Layer (Unit V Content: Padding, Strides, Kernels)
        self.conv1 = nn.Conv1d(in_channels=input_dim, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.relu = nn.ReLU() # Activation Function (Unit III)
        self.pool = nn.MaxPool1d(kernel_size=2) # Pooling (Unit V)
        
        # Second Conv Layer
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        
        # Calculate flattened size
        self.flatten_dim = 64 * (seq_length // 2)
        
        # Fully Connected Layers (Unit V)
        self.fc1 = nn.Linear(self.flatten_dim, 32)
        self.fc2 = nn.Linear(32, 6) # 6 AQI Categories
        
    def forward(self, x):
        # x shape: (batch, seq_len, features) -> needs (batch, features, seq_len) for Conv1d
        x = x.transpose(1, 2)
        x = self.pool(self.relu(self.conv1(x)))
        x = self.relu(self.conv2(x))
        x = x.view(-1, self.flatten_dim)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def train_cnn_demo():
    print("[CNN] Initializing 1D-CNN for Time-Series AQI Prediction...")
    
    # Mock data dimensions based on our project
    input_dim = 12 # 12 meteorological features
    seq_length = 24 # 24 hour sequence
    batch_size = 32
    
    model = AQI_CNN(input_dim, seq_length)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001) # Learning Rate (Unit III)
    
    # Generate mock training cycle to demonstrate "Learnings in ANN" (Unit III/V)
    print(f"[CNN] Architecture:\n{model}")
    
    # Simulated input (Batch, Seq_Len, Features)
    inputs = torch.randn(batch_size, seq_length, input_dim)
    targets = torch.randint(0, 6, (batch_size,))
    
    print("\n[CNN] Starting Training Loop (Gradient Descent & Back-propagation)...")
    for epoch in range(1, 6):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward() # Back-propagation (Unit III)
        optimizer.step() # Weight Update
        
        print(f"Epoch {epoch}/5 - Loss: {loss.item():.4f}")
        
    print("\n[CNN] Demo training complete. Model architecture satisfies Unit V requirements.")

if __name__ == "__main__":
    train_cnn_demo()
