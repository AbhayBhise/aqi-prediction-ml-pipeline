---
title: AQI Prediction ML Pipeline
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# AQI Prediction ML Pipeline

This repository contains the backend Flask API and machine learning models for the AQI Prediction pipeline, running inside a Dockerized container on Hugging Face Spaces.

## Features
- Deep Learning: LSTM & BiLSTM models for AQI sequence forecasting.
- Machine Learning: Ensemble of 9 classification models.
- Generative AI: VAE model for minority class data augmentation.
- Automated API: Flask endpoints serving real-time predictions, analytics, and dynamic EDA.
