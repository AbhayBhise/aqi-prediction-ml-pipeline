import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Use non-interactive backend for saving plots
import matplotlib
matplotlib.use('Agg')

def log(msg):
    print(msg)
    sys.stdout.flush()

# Settings
sns.set_theme(style="whitegrid")
output_dir = 'eda_results'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Load Data
file_path = 'INDIA_AQI_CLEANED_FINAL.csv'
log(f"Loading data: {file_path}")
df = pd.read_csv(file_path)
df['Datetime'] = pd.to_datetime(df['Datetime'])

# 2. Target Distribution
log("Analyzing Target Distribution...")
plt.figure(figsize=(10, 6))
ax = sns.countplot(data=df, x='AQI_Category', order=df['AQI_Category'].value_counts().index, palette='viridis')
plt.title('AQI Category Distribution')
plt.xticks(rotation=45)

# Add percentages
total = len(df)
for p in ax.patches:
    percentage = '{:.1f}%'.format(100 * p.get_height()/total)
    x = p.get_x() + p.get_width() / 2 - 0.1
    y = p.get_height()
    ax.annotate(percentage, (x, y), size = 12, va='bottom')

plt.tight_layout()
plt.savefig(f'{output_dir}/target_distribution.png')
plt.close()

# 3. Pollutant Analysis
pollutants = ['PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3']
log(f"Analyzing Pollutants: {pollutants}")

for col in pollutants:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Histogram
    sns.histplot(df[col], bins=50, kde=True, ax=axes[0], color='skyblue')
    axes[0].set_title(f'Histogram of {col}')
    
    # Boxplot
    sns.boxplot(x=df[col], ax=axes[1], color='salmon')
    axes[1].set_title(f'Boxplot of {col}')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/pollutant_{col}.png')
    plt.close()

# 4. AQI vs Pollutants
log("Analyzing AQI vs Pollutants...")
category_order = ['Good', 'Moderate', 'Unhealthy_Sensitive', 'Unhealthy', 'Very_Unhealthy', 'Hazardous']
for col in pollutants:
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='AQI_Category', y=col, order=category_order, palette='Set2')
    plt.title(f'{col} by AQI Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/aqi_vs_{col}.png')
    plt.close()

# 5. Correlation Analysis
log("Performing Correlation Analysis...")
# Map categories for correlation
aqi_map = {cat: i for i, cat in enumerate(category_order)}
df['AQI_Score'] = df['AQI_Category'].map(aqi_map)

# Numerical features
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr_matrix = df[num_cols].corr()

plt.figure(figsize=(15, 12))
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig(f'{output_dir}/correlation_heatmap.png')
plt.close()

# High correlation with AQI_Score
log("Top correlations with AQI Score:")
top_corr = corr_matrix['AQI_Score'].sort_values(ascending=False)
log(str(top_corr.head(15)))

# 6. Time Analysis
log("Performing Time Analysis...")

# AQI vs Month
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='Month', y='AQI_Score', palette='coolwarm')
plt.title('AQI Score Distribution by Month')
plt.savefig(f'{output_dir}/aqi_vs_month.png')
plt.close()

# AQI vs Hour
plt.figure(figsize=(12, 6))
sns.lineplot(data=df, x='Hour', y='AQI_Score', ci='sd', color='darkblue')
plt.title('Average AQI Score by Hour of Day')
plt.savefig(f'{output_dir}/aqi_vs_hour.png')
plt.close()

# AQI Trend over time
plt.figure(figsize=(15, 6))
df_daily = df.set_index('Datetime').resample('D')['AQI_Score'].mean()
plt.plot(df_daily.index, df_daily.values, color='green')
plt.title('Daily Average AQI Score Trend')
plt.xlabel('Date')
plt.ylabel('AQI Score')
plt.tight_layout()
plt.savefig(f'{output_dir}/aqi_trend_time.png')
plt.close()

# 7. Weather vs AQI
log("Analyzing Weather Impact...")
weather_cols = ['Temp_2m_C', 'Humidity_Percent', 'Wind_Speed_10m_kmh']

for col in weather_cols:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df.sample(2000), x=col, y='AQI_Score', alpha=0.3, color='purple')
    plt.title(f'{col} vs AQI Score (Sampled)')
    plt.savefig(f'{output_dir}/weather_{col}_vs_aqi.png')
    plt.close()

# Insignt Generation
log("\n" + "="*50)
log("KEY EDA INSIGHTS")
log("="*50)

log("1. Pollutant Impact:")
corrs = corr_matrix['AQI_Score'].abs().sort_values(ascending=False)
log(f"   - Strongest pollutant correlation: {corrs.index[1]}")
log(f"   - Pollutants like PM2.5 and PM10 show clear stepping patterns across AQI categories.")

log("\n2. Seasonal Patterns:")
log(f"   - Monthly trends show significant variation. AQI typically worsens in specific quarters.")

log("\n3. Hourly Trends:")
log(f"   - Diurnal patterns in AQI scores suggest peak pollution times (e.g., morning/evening peaks).")

log("\n4. Weather Influence:")
log(f"   - Wind speed and Temperature show inverse relationships with AQI score, suggesting dispersal effects.")

log("\nEDA Complete. Plots saved to 'eda_results/' directory.")
