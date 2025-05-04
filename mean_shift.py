import numpy as np
from sklearn.cluster import MeanShift
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

# === Data Generation ===
n = 6
m = 100
X, _ = make_blobs(n_samples=m, centers=1, n_features=n, random_state=42)

# === Clustering ===
mean_shift = MeanShift()
mean_shift.fit(X)
labels = mean_shift.labels_
cluster_centers = mean_shift.cluster_centers_

st.title("Mean Shift Clustering Viewer")
param = st.slider("Dimension", 0, n-2, 0)  # to allow param and param+1 to exist

st.write(f"Looking at dimensions {param} and {param+1}")

def run():
    # Generate and save plot
    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, param], X[:, param+1], c=labels, cmap='viridis', s=50)
    plt.scatter(cluster_centers[:, param], cluster_centers[:, param+1], 
                c='red', s=200, alpha=0.75, marker='X', label='Centers')
    plt.title(f"Mean Shift Clustering (Dimensions {param} & {param+1})")
    plt.xlabel(f"Dimension {param}")
    plt.ylabel(f"Dimension {param+1}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("mean_shift_clusters.png")
    plt.close()  # Close the figure to avoid memory issues

if st.button("Run Clustering View"):
    run()
    img = Image.open("mean_shift_clusters.png")
    st.image(img, caption=f"Clustering Plot: Dimensions {param} & {param+1}")
