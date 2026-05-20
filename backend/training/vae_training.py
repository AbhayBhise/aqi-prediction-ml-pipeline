"""
Variational Autoencoder (VAE) Training â€” AQI Dataset
Matches the lab assignment: aqi_vae_hyperparameter_tuning.ipynb
Saves all artifacts to backend/results/ for the dashboard.
"""
import os, json, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'INDIA_AQI_COMPLETE_20251126.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 60)
print("AQI VAE Training - Industry Standard Pipeline")
print("=" * 60)

# --- 1. Load Dataset ---
print(f"\n[1/7] Loading dataset from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"      Dataset shape: {df.shape}")

# --- 2. Clean Datetime ---
print("[2/7] Cleaning datetime column...")
df['Datetime'] = pd.to_datetime(df['Datetime'], format='mixed', errors='coerce')
df = df.dropna(subset=['Datetime'])
df = df.sort_values('Datetime')
df = df.ffill().bfill().reset_index(drop=True)
print(f"      Clean dataset: {df.shape}")

# --- 3. Encode AQI Category ---
print("[3/7] Encoding AQI categories...")
le = LabelEncoder()
if 'AQI_Category' in df.columns:
    df['AQI_Label'] = le.fit_transform(df['AQI_Category'].astype(str))
    aqi_labels = df['AQI_Label'].values
    aqi_classes = list(le.classes_)
else:
    df['AQI_Label'] = 0
    aqi_labels = df['AQI_Label'].values
    aqi_classes = ['Unknown']

# --- 4. Select Features & Scale ---
print("[4/7] Scaling features...")
FEATURES = ['PM2_5_ugm3','PM10_ugm3','NO2_ugm3','CO_ugm3','O3_ugm3',
            'Temp_2m_C','Humidity_Percent','Wind_Speed_10m_kmh']
# Only keep features that exist
FEATURES = [f for f in FEATURES if f in df.columns]
X = df[FEATURES].copy()
# Sample for speed (use full for production, 100k for dev)
SAMPLE_SIZE = min(100_000, len(X))
idx = np.random.choice(len(X), SAMPLE_SIZE, replace=False)
X_sample = X.iloc[idx]
labels_sample = aqi_labels[idx]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_sample)
input_dim = X_scaled.shape[1]
print(f"      Feature matrix: {X_scaled.shape}, classes: {aqi_classes}")

# --- 5. Build & Train VAE (TensorFlow) ---
print("[5/7] Building Variational Autoencoder...")
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, backend as K

    tf.get_logger().setLevel('ERROR')

    LATENT_DIM = 8
    EPOCHS = 30
    BATCH_SIZE = 64

    def build_vae(input_dim, latent_dim):
        # Encoder
        encoder_inputs = keras.Input(shape=(input_dim,), name="encoder_input")
        x = layers.Dense(64, activation="relu", name="enc_dense1")(encoder_inputs)
        x = layers.Dense(32, activation="relu", name="enc_dense2")(x)
        z_mean = layers.Dense(latent_dim, name="z_mean")(x)
        z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)

        # Sampling layer
        def sampling(args):
            z_m, z_lv = args
            eps = tf.random.normal(shape=(tf.shape(z_m)[0], latent_dim))
            return z_m + tf.exp(0.5 * z_lv) * eps

        z = layers.Lambda(sampling, name="z")([z_mean, z_log_var])
        encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name="encoder")

        # Decoder
        latent_inputs = keras.Input(shape=(latent_dim,), name="decoder_input")
        x = layers.Dense(32, activation="relu", name="dec_dense1")(latent_inputs)
        x = layers.Dense(64, activation="relu", name="dec_dense2")(x)
        decoder_outputs = layers.Dense(input_dim, name="decoder_output")(x)
        decoder = keras.Model(latent_inputs, decoder_outputs, name="decoder")

        # VAE
        class VAE(keras.Model):
            def __init__(self, enc, dec, **kwargs):
                super().__init__(**kwargs)
                self.encoder = enc
                self.decoder = dec
                self.total_loss_tracker = keras.metrics.Mean(name="loss")
                self.recon_loss_tracker = keras.metrics.Mean(name="reconstruction_loss")
                self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

            @property
            def metrics(self):
                return [self.total_loss_tracker, self.recon_loss_tracker, self.kl_loss_tracker]

            def train_step(self, data):
                with tf.GradientTape() as tape:
                    z_m, z_lv, z_s = self.encoder(data)
                    reconstruction = self.decoder(z_s)
                    recon_loss = tf.reduce_mean(keras.losses.mse(data, reconstruction))
                    kl_loss = -0.5 * tf.reduce_mean(
                        tf.reduce_sum(1 + z_lv - tf.square(z_m) - tf.exp(z_lv), axis=1)
                    )
                    total_loss = recon_loss + 0.001 * kl_loss  # beta-VAE: small KL weight
                grads = tape.gradient(total_loss, self.trainable_weights)
                self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
                self.total_loss_tracker.update_state(total_loss)
                self.recon_loss_tracker.update_state(recon_loss)
                self.kl_loss_tracker.update_state(kl_loss)
                return {"loss": self.total_loss_tracker.result(),
                        "reconstruction_loss": self.recon_loss_tracker.result(),
                        "kl_loss": self.kl_loss_tracker.result()}

        vae_model = VAE(encoder, decoder, name="vae")
        vae_model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001))
        return vae_model, encoder, decoder

    vae, encoder, decoder = build_vae(input_dim, LATENT_DIM)
    print(f"      VAE built â€” latent_dim={LATENT_DIM}, params: {vae.encoder.count_params() + vae.decoder.count_params():,}")

    # Train
    print(f"      Training for {EPOCHS} epochs on {SAMPLE_SIZE:,} samples...")
    history = vae.fit(X_scaled, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)

    # Save training history
    history_data = {
        "epochs": list(range(1, EPOCHS + 1)),
        "loss": [float(v) for v in history.history['loss']],
        "reconstruction_loss": [float(v) for v in history.history['reconstruction_loss']],
        "kl_loss": [float(v) for v in history.history['kl_loss']],
        "latent_dim": LATENT_DIM,
        "batch_size": BATCH_SIZE,
        "sample_size": SAMPLE_SIZE,
        "input_features": FEATURES,
        "architecture": {
            "encoder": "Input(8) â†’ Dense(64,relu) â†’ Dense(32,relu) â†’ z_mean(8) + z_log_var(8)",
            "decoder": "z(8) â†’ Dense(32,relu) â†’ Dense(64,relu) â†’ Output(8)",
            "total_params": vae.encoder.count_params() + vae.decoder.count_params()
        }
    }
    with open(os.path.join(RESULTS_DIR, 'vae_training_history.json'), 'w') as f:
        json.dump(history_data, f, indent=2)
    print("      âœ“ Training history saved.")

    # --- 6. Hyperparameter Tuning ---
    print("[6/7] Hyperparameter tuning grid search...")
    latent_options = [4, 8, 16]
    batch_options = [32, 64]
    tuning_results = []

    for latent in latent_options:
        for batch in batch_options:
            print(f"      Testing latent={latent}, batch={batch}...")
            enc_inputs = keras.Input(shape=(input_dim,))
            hx = layers.Dense(64, activation='relu')(enc_inputs)
            hx = layers.Dense(32, activation='relu')(hx)
            hz_mean = layers.Dense(latent)(hx)
            hz_log = layers.Dense(latent)(hx)

            def _sample(args):
                m, lv = args
                return m + tf.exp(0.5 * lv) * tf.random.normal(shape=tf.shape(m))

            hz = layers.Lambda(_sample)([hz_mean, hz_log])
            dx = layers.Dense(32, activation='relu')(hz)
            dx = layers.Dense(64, activation='relu')(dx)
            dout = layers.Dense(input_dim)(dx)
            mini_vae = keras.Model(enc_inputs, dout)
            mini_vae.compile(optimizer='adam', loss='mse')
            h = mini_vae.fit(X_scaled, X_scaled, epochs=5, batch_size=batch, verbose=0)
            final_loss = float(h.history['loss'][-1])
            tuning_results.append({
                "latent_dim": latent,
                "batch_size": batch,
                "final_loss": round(final_loss, 6),
                "config_label": f"latent={latent}, batch={batch}"
            })
            print(f"        loss={final_loss:.4f}")

    # Find best config
    best = min(tuning_results, key=lambda x: x['final_loss'])
    tuning_output = {"results": tuning_results, "best_config": best}
    with open(os.path.join(RESULTS_DIR, 'vae_hyperparameter_results.json'), 'w') as f:
        json.dump(tuning_output, f, indent=2)
    print(f"      âœ“ Best config: {best['config_label']} (loss={best['final_loss']})")

    # --- 7. Generate Plots ---
    print("[7/7] Generating visualizations...")

    # 7a. Training Loss Curve
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('#0F172A')
    for ax in axes:
        ax.set_facecolor('#1E293B')
        ax.tick_params(colors='#94A3B8')
        ax.spines[:].set_color('#334155')

    epochs_range = history_data['epochs']
    axes[0].plot(epochs_range, history_data['loss'], color='#6366F1', linewidth=2.5, label='Total Loss')
    axes[0].plot(epochs_range, history_data['reconstruction_loss'], color='#22D3EE', linewidth=2, linestyle='--', label='Reconstruction Loss')
    axes[0].set_title('VAE Training Loss', color='white', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch', color='#94A3B8')
    axes[0].set_ylabel('Loss', color='#94A3B8')
    axes[0].legend(framealpha=0.3, labelcolor='white')
    axes[0].grid(True, alpha=0.2, color='#334155')

    # KL Loss
    axes[1].plot(epochs_range, history_data['kl_loss'], color='#F59E0B', linewidth=2.5, label='KL Divergence Loss')
    axes[1].set_title('KL Divergence per Epoch', color='white', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch', color='#94A3B8')
    axes[1].set_ylabel('KL Loss', color='#94A3B8')
    axes[1].legend(framealpha=0.3, labelcolor='white')
    axes[1].grid(True, alpha=0.2, color='#334155')

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'vae_loss_curve.png'), dpi=120, bbox_inches='tight', facecolor='#0F172A')
    plt.close()
    print("      âœ“ vae_loss_curve.png saved.")

    # 7b. Hyperparameter Tuning Heatmap
    import numpy as np
    latents = latent_options
    batches = batch_options
    loss_matrix = np.zeros((len(latents), len(batches)))
    for r in tuning_results:
        i = latents.index(r['latent_dim'])
        j = batches.index(r['batch_size'])
        loss_matrix[i, j] = r['final_loss']

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#1E293B')
    im = ax.imshow(loss_matrix, cmap='YlOrRd_r', aspect='auto')
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.tick_params(colors='white')
    cbar.set_label('Reconstruction Loss', color='white')
    ax.set_xticks(range(len(batches)))
    ax.set_yticks(range(len(latents)))
    ax.set_xticklabels([f'batch={b}' for b in batches], color='white')
    ax.set_yticklabels([f'latent={l}' for l in latents], color='white')
    ax.set_title('Hyperparameter Tuning Grid', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Batch Size', color='#94A3B8')
    ax.set_ylabel('Latent Dimension', color='#94A3B8')
    for i in range(len(latents)):
        for j in range(len(batches)):
            is_best = (latents[i] == best['latent_dim'] and batches[j] == best['batch_size'])
            txt = ax.text(j, i, f"{loss_matrix[i,j]:.4f}", ha='center', va='center',
                         color='white', fontsize=11, fontweight='bold' if is_best else 'normal')
            if is_best:
                ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='#22D3EE', linewidth=3))
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'vae_hyperparameter_grid.png'), dpi=120, bbox_inches='tight', facecolor='#0F172A')
    plt.close()
    print("      âœ“ vae_hyperparameter_grid.png saved.")

    # 7c. Latent Space Visualization (PCA of z vectors)
    from sklearn.decomposition import PCA
    _, _, z_vecs = encoder.predict(X_scaled, verbose=0)
    pca = PCA(n_components=2)
    z_2d = pca.fit_transform(z_vecs)

    aqi_colors = {'Good': '#22C55E', 'Moderate': '#EAB308', 'Unhealthy for Sensitive Groups': '#F97316',
                  'Unhealthy': '#EF4444', 'Very Unhealthy': '#A855F7', 'Hazardous': '#7F1D1D',
                  'Unknown': '#64748B'}
    label_names = [aqi_classes[l] if l < len(aqi_classes) else 'Unknown' for l in labels_sample]

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#1E293B')
    for cls in aqi_classes:
        mask = np.array(label_names) == cls
        if mask.sum() > 0:
            color = aqi_colors.get(cls, '#64748B')
            ax.scatter(z_2d[mask, 0], z_2d[mask, 1], c=color, label=cls,
                      alpha=0.4, s=8, edgecolors='none')
    ax.set_title('VAE Latent Space (PCA 2D Projection)', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)', color='#94A3B8')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)', color='#94A3B8')
    ax.tick_params(colors='#94A3B8')
    ax.spines[:].set_color('#334155')
    ax.legend(framealpha=0.3, labelcolor='white', markerscale=3, fontsize=9)
    ax.grid(True, alpha=0.15, color='#334155')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'vae_latent_space.png'), dpi=120, bbox_inches='tight', facecolor='#0F172A')
    plt.close()
    print("      âœ“ vae_latent_space.png saved.")

    # 7d. Real vs Synthetic Distribution
    N_GENERATED = 2746
    z_sample = np.random.normal(size=(N_GENERATED, LATENT_DIM))
    generated_data = decoder.predict(z_sample, verbose=0)
    generated_data_unscaled = scaler.inverse_transform(generated_data)
    real_pm25 = X_sample[FEATURES[0]].values  # PM2.5

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0F172A')
    feature_labels = ['PM2.5', 'PM10', 'NO2', 'CO', 'O3', 'Temperature', 'Humidity', 'Wind Speed']

    # PM2.5 distribution
    axes[0].set_facecolor('#1E293B')
    axes[0].hist(real_pm25, bins=50, alpha=0.7, color='#6366F1', label='Real PM2.5', density=True)
    axes[0].hist(generated_data_unscaled[:, 0], bins=50, alpha=0.7, color='#22D3EE', label='Synthetic PM2.5', density=True)
    axes[0].set_title('Real vs. Synthetic PM2.5 Distribution', color='white', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('PM2.5 (Î¼g/mÂ³)', color='#94A3B8')
    axes[0].set_ylabel('Density', color='#94A3B8')
    axes[0].tick_params(colors='#94A3B8')
    axes[0].spines[:].set_color('#334155')
    axes[0].legend(framealpha=0.3, labelcolor='white')
    axes[0].grid(True, alpha=0.2, color='#334155')

    # Feature-wise mean comparison
    real_means = X_sample[FEATURES].mean().values
    gen_means = generated_data_unscaled.mean(axis=0)
    x_pos = np.arange(len(FEATURES))
    axes[1].set_facecolor('#1E293B')
    axes[1].bar(x_pos - 0.2, real_means, 0.4, label='Real', color='#6366F1', alpha=0.85)
    axes[1].bar(x_pos + 0.2, gen_means, 0.4, label='Synthetic', color='#22D3EE', alpha=0.85)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(feature_labels, rotation=30, ha='right', color='#94A3B8', fontsize=8)
    axes[1].set_title('Feature Mean: Real vs. Synthetic', color='white', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Mean Value', color='#94A3B8')
    axes[1].tick_params(colors='#94A3B8')
    axes[1].spines[:].set_color('#334155')
    axes[1].legend(framealpha=0.3, labelcolor='white')
    axes[1].grid(True, alpha=0.2, color='#334155', axis='y')

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'vae_real_vs_synthetic.png'), dpi=120, bbox_inches='tight', facecolor='#0F172A')
    plt.close()
    print("      âœ“ vae_real_vs_synthetic.png saved.")

    # Save generation stats
    gen_stats = {
        "n_generated": N_GENERATED,
        "latent_dim_used": LATENT_DIM,
        "best_config": best,
        "generated_pm25_mean": float(generated_data_unscaled[:, 0].mean()),
        "generated_pm25_std": float(generated_data_unscaled[:, 0].std()),
        "real_pm25_mean": float(real_pm25.mean()),
        "real_pm25_std": float(real_pm25.std()),
        "pca_variance_explained": [float(v) for v in pca.explained_variance_ratio_],
        "artifacts": [
            "vae_loss_curve.png",
            "vae_hyperparameter_grid.png",
            "vae_latent_space.png",
            "vae_real_vs_synthetic.png"
        ]
    }
    with open(os.path.join(RESULTS_DIR, 'vae_generation_stats.json'), 'w') as f:
        json.dump(gen_stats, f, indent=2)

    print("\n" + "=" * 60)
    print("âœ“ VAE Training Complete! All artifacts saved to backend/results/")
    print(f"  Best config: {best['config_label']} | Final loss: {best['final_loss']}")
    print("=" * 60)

except ImportError:
    print("\n[ERROR] TensorFlow not found. Install with:")
    print("  pip install tensorflow")
    sys.exit(1)

