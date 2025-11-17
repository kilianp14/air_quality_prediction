# Air Quality Prediction Service
**Daily PM 2.5 Forecasts using Hopsworks, GitHub Actions, and GitHub Pages**

This project builds a fully automated machine-learning forecasting pipeline for **PM 2.5 air quality** across four different cities in Värmland, Sweden.  
It generates prediction plots every day (forecast & hindcast) and publishes them to a public dashboard.

---

##  Project Overview

We forecast **next-7-days PM2.5 values** for several cities.  
For each city we generate:

- **Forecast plots** (future predictions)
- **Hindcast plots** (retrospective accuracy against real observations)

The predictions power a **public GitHub Pages dashboard** with interactive dropdowns:
- Select **city**
- Select **model type** → *Base* or *Lagged*
- Display:
    - Forecast image
    - Hindcast image

---

## Models

We train **two XGBoost regression models**:

### 1. **Base Model**
Uses only *meteorological features* (no historical PM 2.5).

**Features:**
- temperature_2m_mean
- precipitation_sum
- wind_speed_10m_max
- wind_direction_10m_dominant
- city

---

### 2. **Lagged Model**
Enhances the Base Model by including **historical air quality**:

**Additional Features:**
- lagged_1  (yesterday’s PM 2.5)
- lagged_2
- lagged_3

The model predicts PM 2.5 based on weather + last 3 days of measurements.

**Benefits:**
- Much higher accuracy when lagged data exists
- Mean square error for training data went from 9.84638 for the base model to 3.9555526 for the lagged model.
- Mean square error for test data went from 96.95265 to 48.87036 for the lagged model.

We maintain the data used to train these models in a **Hopsworks Feature Store** using two Feature Views:


### Weather Feature View
- temperature_2m_mean
- precipitation_sum
- wind_speed_10m_max
- wind_speed_10m_max
- date
- city

### Air Quality Feature View
- pm25
- lagged_1
- lagged_2
- lagged_3
- city
- street

---

# Procedures

## 1. Feature Backfill

1_air_quality_backfill.ipynb is used to load historical PM 2.5 data downloaded in csv format
from ACIQN, as well as historical weather data from OpenMeteo and store it in a Hopsworks Feature Store.
We needed to perform a transformation on the historical data retrieved from the CSV files to match the data format we
got from the API. More specifically, we multiplied the PM 2.5 values by 4.2

## 2. Feature pipeline

2_air_quality_feature_pipeline.ipynb is used to download daily data from ACIQN
and OpenMeteo and store it in the Hopsworks Feature Groups. It retrieves the daily
PM 2.5 value and weather predictions for the next 7 days.
It is scheduled to run daily, using GitHub Actions.

## 3. Training pipeline

3_air_quality_training_pipeline.ipynb is used to train the two models using the historical data
and store them in the Hopsworks Model Registry. We create one feature view per model. Then we use `.train_test_split()`
to generate training and test data. We then train the models and evaluate them against the test data.
We plot the hindcasts for the historical data for each model.
Lastly, we store the models in the Hopsworks Model Registry.

## 4. Inference Pipeline

4_air_quality_batch_inference.ipynb is used to generate forecasts for the predicted weather data that
we have in our Feature Store. It downloads the models from the model registry and then uses them to predict
the next 7 days of PM 2.5 values.
It is scheduled to run daily, alongside the Feature Pipeline, using GitHub Actions.
After this, there is a step to push all generated images to the repository,
so they can be picked up by the GitHub Pages deployment process.

---

## Dashboard (GitHub Pages)

A static HTML page allows users to explore the forecasts:

- Users select a model out of the two available options: **base** or **lagged**
- Users select a city from the dropdown menu
- The forecast image and hindcast image are displayed

GitHub Actions publishes updates automatically when new images arrive.

