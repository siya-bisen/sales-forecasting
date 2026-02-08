import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of data points
n_points = 5000

# Generate date range
dates = pd.date_range(start="2010-01-01", periods=n_points, freq="D")

# Components
trend = np.linspace(50, 300, n_points)                 # upward trend
weekly_seasonality = 20 * np.sin(2 * np.pi * np.arange(n_points) / 7)
yearly_seasonality = 40 * np.sin(2 * np.pi * np.arange(n_points) / 365)
noise = np.random.normal(0, 15, n_points)              # random noise

# Sales generation
sales = trend + weekly_seasonality + yearly_seasonality + noise

# Ensure no negative sales
sales = np.maximum(0, sales).round(2)

# Create DataFrame
df = pd.DataFrame({
    "Date": dates,
    "Sales": sales
})

# Save to CSV
df.to_csv("sales_data.csv", index=False)

print(df.head())
print(f"\nDataset generated with {len(df)} rows.")