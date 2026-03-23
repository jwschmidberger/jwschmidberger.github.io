---
title: Titanic Survival Neural Network
summary: Kaggle challenge build predicting survival with Keras
tech:
  - Python
  - Keras
  - Neural networks
links:
  - label: PDF Notebook
    url: /pdfs/210511_NN_v3.pdf
---

Using Kaggle's classic Titanic dataset I built a lightweight neural-network classifier in Python/Keras to predict passenger survival. After a few rounds of feature engineering (fare binning, one-hot encoding for cabins and titles) and dropout tuning, the model steadily improved to **~78% accuracy on the public leaderboard**.

The notebook (linked above) walks through the full workflow—data cleaning, exploratory analysis, model architecture, and evaluation. I keep iterating on this project to compare modern architectures (TabNet, gradient boosting) against the baseline dense network.
