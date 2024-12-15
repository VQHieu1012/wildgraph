import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np

# Example function to plot trajectories for different models
def plot_trajectories(models_data, model_names, real_samples, map_boundary, save_path=None):
    """
    Plots trajectories for different models along with real samples.

    :param models_data: List of model trajectories. Each item is a list of trajectories (lat, long).
    :param model_names: Names of the models (to label subplots).
    :param real_samples: Real trajectory data (list of (lat, long) points).
    :param map_boundary: Tuple (min_lon, max_lon, min_lat, max_lat) to set map bounds.
    :param save_path: Path to save the plot image (optional).
    """
    num_models = len(models_data)
    cols = 3  # Number of columns in the grid
    rows = (num_models + 1) // cols + 1  # Including real samples
    fig, axs = plt.subplots(rows, cols, figsize=(15, 10))
    axs = axs.flatten()

    # Plot real samples
    ax = axs[0]
    for traj in real_samples:
        traj = np.array(traj)
        ax.plot(traj[:, 1], traj[:, 0], alpha=0.5, color='blue')
    ax.set_title("Real Samples")
    ax.set_xlim(map_boundary[0], map_boundary[1])
    ax.set_ylim(map_boundary[2], map_boundary[3])

    # Plot model-generated trajectories
    for i, (data, name) in enumerate(zip(models_data, model_names), start=1):
        ax = axs[i]
        for traj in data:
            traj = np.array(traj)
            ax.plot(traj[:, 1], traj[:, 0], alpha=0.5)
        ax.set_title(name)
        ax.set_xlim(map_boundary[0], map_boundary[1])
        ax.set_ylim(map_boundary[2], map_boundary[3])

    # Hide unused subplots
    for ax in axs[len(models_data) + 1:]:
        ax.axis('off')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

# Example usage
# Replace the following with actual data
map_boundary = (-30, 60, 40, 75)  # (min_lon, max_lon, min_lat, max_lat)
real_samples = [
    np.random.uniform([50, -20], [70, 40], size=(100, 2)) for _ in range(10)
]  # Replace with real data
models_data = [
    [np.random.uniform([50, -20], [70, 40], size=(100, 2)) for _ in range(10)]  # WildGraph
    for _ in range(5)
]  # Replace with actual model data
model_names = ["WildGraph", "WildGraph-Transformers", "WildGEN", "VAE", "GAN"]

plot_trajectories(models_data, model_names, real_samples, map_boundary)
