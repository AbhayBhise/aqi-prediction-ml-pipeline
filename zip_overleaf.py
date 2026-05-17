import zipfile
import os

def create_overleaf_zip():
    zip_path = 'IEEE_AQI_Research_Paper.zip'
    files_to_zip = [
        ('paper.tex', 'paper.tex'),
        ('backend/results/correlation_heatmap.png', 'backend/results/correlation_heatmap.png'),
        ('backend/results/pca_clusters.png', 'backend/results/pca_clusters.png'),
        ('backend/results/vae_loss_curve.png', 'backend/results/vae_loss_curve.png'),
        ('backend/results/sequential_comparison_plot.png', 'backend/results/sequential_comparison_plot.png')
    ]
    
    print(f"Creating {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for local_path, arc_path in files_to_zip:
            if os.path.exists(local_path):
                zipf.write(local_path, arc_path)
                print(f"Successfully added: {local_path} -> {arc_path}")
            else:
                print(f"Error: Required file {local_path} not found!")

if __name__ == '__main__':
    create_overleaf_zip()
