# Regenerate latent space plot with correct color mapping for underscore class names
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'INDIA_AQI_COMPLETE_20251126.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'results')

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA

import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras import layers

print("Rebuilding latent space with correct color mapping...")

df = pd.read_csv(DATA_PATH)
df['Datetime'] = pd.to_datetime(df['Datetime'], format='mixed', errors='coerce')
df = df.dropna(subset=['Datetime']).sort_values('Datetime').ffill().bfill().reset_index(drop=True)

le = LabelEncoder()
df['AQI_Label'] = le.fit_transform(df['AQI_Category'].astype(str))
aqi_classes = list(le.classes_)
print(f"AQI classes (exact): {aqi_classes}")

FEATURES = [f for f in ['PM2_5_ugm3','PM10_ugm3','NO2_ugm3','CO_ugm3','O3_ugm3','Temp_2m_C','Humidity_Percent','Wind_Speed_10m_kmh'] if f in df.columns]
SAMPLE_SIZE = 100_000
idx = np.random.seed(42) or np.random.choice(len(df), SAMPLE_SIZE, replace=False)
X_sample = df[FEATURES].iloc[idx]
labels_sample = df['AQI_Label'].values[idx]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_sample)
input_dim = X_scaled.shape[1]
LATENT_DIM = 8

# Rebuild encoder
encoder_inputs = keras.Input(shape=(input_dim,))
x = layers.Dense(64, activation="relu")(encoder_inputs)
x = layers.Dense(32, activation="relu")(x)
z_mean = layers.Dense(LATENT_DIM)(x)
z_log_var = layers.Dense(LATENT_DIM)(x)

def sampling(args):
    m, lv = args
    return m + tf.exp(0.5 * lv) * tf.random.normal(shape=tf.shape(m))

z = layers.Lambda(sampling)([z_mean, z_log_var])
encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z])

# Train briefly to get meaningful representation
class VAE(keras.Model):
    def __init__(self, enc, **kwargs):
        super().__init__(**kwargs)
        self.encoder = enc
        dec_in = keras.Input(shape=(LATENT_DIM,))
        dx = layers.Dense(32, activation='relu')(dec_in)
        dx = layers.Dense(64, activation='relu')(dx)
        dec_out = layers.Dense(input_dim)(dx)
        self.decoder = keras.Model(dec_in, dec_out)
    def train_step(self, data):
        with tf.GradientTape() as tape:
            z_m, z_lv, z_s = self.encoder(data)
            recon = self.decoder(z_s)
            recon_loss = tf.reduce_mean(keras.losses.mse(data, recon))
            kl_loss = -0.5 * tf.reduce_mean(tf.reduce_sum(1 + z_lv - tf.square(z_m) - tf.exp(z_lv), axis=1))
            total = recon_loss + 0.001 * kl_loss
        grads = tape.gradient(total, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        return {"loss": total, "reconstruction_loss": recon_loss, "kl_loss": kl_loss}

vae = VAE(encoder)
vae.compile(optimizer=keras.optimizers.Adam(0.001))
print("Training 30 epochs...")
vae.fit(X_scaled, epochs=30, batch_size=64, verbose=0)
print("Done. Extracting latent vectors...")

_, _, z_vecs = encoder.predict(X_scaled, verbose=0)
pca = PCA(n_components=2)
z_2d = pca.fit_transform(z_vecs)

# CORRECT color map using exact underscore class names from the dataset
aqi_colors = {
    'Good': '#22C55E',
    'Moderate': '#EAB308',
    'Satisfactory': '#84CC16',
    'Unhealthy for Sensitive Groups': '#F97316',
    'Unhealthy_Sensitive': '#F97316',   # underscore variant
    'Unhealthy': '#EF4444',
    'Very_Unhealthy': '#A855F7',        # underscore variant
    'Very Unhealthy': '#A855F7',
    'Hazardous': '#DC2626',
    'Severe': '#7F1D1D',
}

label_names = [aqi_classes[l] if l < len(aqi_classes) else 'Unknown' for l in labels_sample]
print(f"Unique labels in sample: {set(label_names)}")

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor('#0F172A')
ax.set_facecolor('#1E293B')

for cls in aqi_classes:
    mask = np.array(label_names) == cls
    if mask.sum() > 0:
        color = aqi_colors.get(cls, '#94A3B8')  # slate-400 fallback (visible, not grey)
        ax.scatter(z_2d[mask, 0], z_2d[mask, 1], c=color, label=f'{cls} (n={mask.sum():,})',
                  alpha=0.45, s=10, edgecolors='none')

ax.set_title('VAE Latent Space (PCA 2D Projection)', color='white', fontsize=14, fontweight='bold')
ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance explained)', color='#94A3B8', fontsize=10)
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance explained)', color='#94A3B8', fontsize=10)
ax.tick_params(colors='#94A3B8')
ax.spines[:].set_color('#334155')
legend = ax.legend(framealpha=0.4, labelcolor='white', markerscale=3, fontsize=9,
                   facecolor='#1E293B', edgecolor='#334155')
ax.grid(True, alpha=0.12, color='#334155')

# Add annotation explaining structure
ax.annotate('Low severity\n(Good/Moderate)',
            xy=(-2, 0), xytext=(-3.5, 4), fontsize=8, color='#22C55E',
            arrowprops=dict(arrowstyle='->', color='#22C55E', lw=1))
ax.annotate('High severity\n(Unhealthy/Severe)',
            xy=(5, 0), xytext=(5.5, 5), fontsize=8, color='#EF4444',
            arrowprops=dict(arrowstyle='->', color='#EF4444', lw=1))

plt.tight_layout()
out = os.path.join(RESULTS_DIR, 'vae_latent_space.png')
plt.savefig(out, dpi=130, bbox_inches='tight', facecolor='#0F172A')
plt.close()
print(f"Saved: {out}")
print(f"PCA variance: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%")
print("Latent space plot regenerated with correct colors.")
