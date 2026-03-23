---
title: edX Data Science Professional Certificate
summary: Nine-module R program capped with two ML projects
tech:
  - R
  - Tidyverse
  - Machine Learning
links:
  - label: Course Overview
    url: https://courses.edx.org/dashboard/programs/3c32e3e0-b6fe-4ee4-bd4f-210c6339e074/
---

After nine modules covering wrangling, inference, and ML with R, the edX program culminated in two capstone projects that I used to demonstrate modeling depth and documentation rigor.

## Project 1 · MovieLens Recommender
- Built a layered recommender system on the MovieLens dataset, progressively adding baseline, user, movie, and temporal effects.
- Tuned regularization terms to keep RMSE low on the validation split; final model achieved **0.8602 RMSE**.
- Full report: [PDF](/pdfs/200328_Capstone_sub.pdf) · [R Markdown](/pdfs/200328_Capstone_sub.Rmd)

## Project 2 · Credit Card Fraud Detection
- Tackled a highly imbalanced European transaction set (2013) by pairing SMOTE resampling with cost-sensitive learning to minimize false negatives.
- Explored PCA components (V1–V28) supplied with the dataset to interpret the separation between fraudulent and legitimate behaviour.
- Delivered [a narrative report](/pdfs/200529_creditcard3.pdf) plus the [Rmd notebook](/pdfs/200529_creditcard3.Rmd).
- Final tuned random-forest pipeline caught **100% of known fraud cases** with only 33 false positives across 25K transactions.

The write-ups include visual diagnostics (transaction value vs. time, inter-transaction intervals, PCA projections) and detail my approach to stakeholder-friendly reporting.
