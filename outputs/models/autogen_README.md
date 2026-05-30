# Data Stewardship Experiment: Model Deposit

## Contents
- `rf_model.rds`: Trained Random Forest model (ranger implementation)
- `lm_model.rds`: Trained Linear Regression model
- `lmm_model.rds`: Trained Nested Linear Mixed Model
- `all_models.RData`: All three models bundled together
- `test_predictions.csv`: Test set predictions from all models
- `rf_model_fair4ml.json`: FAIR4ML metadata for Random Forest
- `lm_model_fair4ml.json`: FAIR4ML metadata for Linear Regression
- `lmm_model_fair4ml.json`: FAIR4ML metadata for Linear Mixed Model
- `ro-crate-metadata.json`: RO-Crate metadata referencing all models

## Model Summary
Random Forest RMSE: 31249340027.01
Linear Model RMSE: 6272378553.33
Mixed Model RMSE: 6208319190.05

## Reproduction Instructions
1. Load the models using readRDS()
2. Ensure required packages are installed (ranger, lme4, tidymodels)
3. See FAIR4ML metadata for complete hyperparameters and limitations
4. Refer to session_info.txt for complete software environment

## FAIR4ML Compliance
All metadata files follow FAIR4ML standards for Findable, Accessible,
    Interoperable, and Reusable machine learning models.

## Deposit Information
Deposited in TUWRD (T3.9) on: 2026-05-30T20:50:22+0200
Dataset DOI: 10.82556/pbwe-bk06
Contact: TU Wien Research Data Management
