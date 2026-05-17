"""
Generates 4 consolidated EDA images directly into model_results/
for serving via Flask /images/<filename> route.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

OUTPUT_DIR = 'model_results'
os.makedirs(OUTPUT_DIR, exist_ok=True)
sns.set_theme(style='darkgrid', palette='deep')

print("Loading data...")
df = pd.read_csv('INDIA_AQI_CLEANED_FINAL.csv')
df['Datetime'] = pd.to_datetime(df['Datetime'])
print(f"Loaded: {df.shape}")

pollutants = ['PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3']
category_order = ['Good', 'Moderate', 'Unhealthy_Sensitive', 'Unhealthy', 'Very_Unhealthy', 'Hazardous']
aqi_map = {cat: i for i, cat in enumerate(category_order)}

# -----------------------------------------------------------------
# 1. pollutant_histograms.png  — 2×3 grid of pollutant distributions
# -----------------------------------------------------------------
print("Generating pollutant_histograms.png ...")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('Pollutant Concentration Distributions', fontsize=16, fontweight='bold')
colors = ['#6366f1', '#14b8a6', '#f59e0b', '#ef4444', '#8b5cf6', '#10b981']
for ax, col, color in zip(axes.flat, pollutants, colors):
    sample = df[col].dropna().sample(min(50000, len(df)), random_state=42)
    ax.hist(sample, bins=60, color=color, alpha=0.8, edgecolor='none')
    ax.set_title(col.replace('_ugm3', '').replace('_', ' '), fontweight='bold')
    ax.set_xlabel('Concentration')
    ax.set_ylabel('Frequency')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/pollutant_histograms.png', dpi=100, bbox_inches='tight')
plt.close()
print("  Saved.")

# -----------------------------------------------------------------
# 2. aqi_boxplots.png  — boxplots of each pollutant per AQI category
# -----------------------------------------------------------------
print("Generating aqi_boxplots.png ...")
sample_df = df.dropna(subset=pollutants + ['AQI_Category']).sample(min(80000, len(df)), random_state=42)
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Pollutant Levels by AQI Category', fontsize=16, fontweight='bold')
for ax, col in zip(axes.flat, pollutants):
    sns.boxplot(
        data=sample_df, x='AQI_Category', y=col,
        order=[c for c in category_order if c in sample_df['AQI_Category'].unique()],
        palette='Set2', ax=ax, showfliers=False
    )
    ax.set_title(col.replace('_ugm3', ''), fontweight='bold')
    ax.set_xlabel('')
    ax.tick_params(axis='x', rotation=30)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/aqi_boxplots.png', dpi=100, bbox_inches='tight')
plt.close()
print("  Saved.")

# -----------------------------------------------------------------
# 3. correlation_heatmap.png
# -----------------------------------------------------------------
print("Generating correlation_heatmap.png ...")
df['AQI_Score'] = df['AQI_Category'].map(aqi_map)
num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != 'AQI_Score']
# Use only key features to keep heatmap readable
key_cols = pollutants + ['Temp_2m_C', 'Humidity_Percent', 'Wind_Speed_10m_kmh', 'Hour', 'Month', 'AQI_Score']
key_cols = [c for c in key_cols if c in df.columns]
corr = df[key_cols].corr()
fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
            linewidths=0.5, ax=ax, annot_kws={'size': 9})
ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/correlation_heatmap.png', dpi=100, bbox_inches='tight')
plt.close()
print("  Saved.")

# -----------------------------------------------------------------
# 4. time_trends.png  — AQI by hour + AQI by month
# -----------------------------------------------------------------
print("Generating time_trends.png ...")
df['AQI_Score'] = df['AQI_Category'].map(aqi_map)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Temporal AQI Trends', fontsize=14, fontweight='bold')

# By hour
hourly = df.groupby('Hour')['AQI_Score'].mean()
axes[0].plot(hourly.index, hourly.values, color='#6366f1', linewidth=2.5, marker='o', markersize=4)
axes[0].fill_between(hourly.index, hourly.values, alpha=0.15, color='#6366f1')
axes[0].set_title('Avg AQI Score by Hour of Day')
axes[0].set_xlabel('Hour')
axes[0].set_ylabel('Avg AQI Score')
axes[0].set_xticks(range(0, 24, 2))

# By month
monthly = df.groupby('Month')['AQI_Score'].mean()
axes[1].bar(monthly.index, monthly.values, color='#14b8a6', alpha=0.85, edgecolor='none')
axes[1].set_title('Avg AQI Score by Month')
axes[1].set_xlabel('Month')
axes[1].set_ylabel('Avg AQI Score')
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], rotation=30)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/time_trends.png', dpi=100, bbox_inches='tight')
plt.close()
print("  Saved.")

print("\nAll 4 EDA images generated successfully in model_results/")
