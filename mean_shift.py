import numpy as np
from sklearn.cluster import MeanShift
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

n = 6
m = 100 

X, _ = make_blobs(n_samples=m, centers=1, n_features=n, random_state=42)

# === Step 2: Apply Mean Shift Clustering ===
mean_shift = MeanShift()
mean_shift.fit(X)
labels = mean_shift.labels_
cluster_centers = mean_shift.cluster_centers_

print(f"Number of clusters found: {len(np.unique(labels))}")
print("Cluster centers:\n", cluster_centers)

# === Step 3: (Optional) Plot if dimensions allow ===


import streamlit as st
from PIL import Image

st.title("Image Viewer with Actions")


param = st.slider("Dimension", 0, 5, 1)
st.write("Looking: ", param, " and ", param+1, " dimensions")

def run():
    if n >= 2+param:
        plt.figure(figsize=(8, 6))
        plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', s=50)
        plt.scatter(cluster_centers[:, 0], cluster_centers[:, 1], 
                    c='red', s=200, alpha=0.75, marker='X', label='Centers')
        plt.title("Mean Shift Clustering (First 2 Dimensions)")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.legend()
        plt.grid(True)
        plt.savefig("mean_shift_clusters.png")

    else:
        print("Plotting skipped (requires at least 2 dimensions)")
if st.button("Action 1"):
    run()
    img = Image.open("mean_shift_clusters.png")
    st.image(img, caption=f"Current image: {st.session_state.current_image}")
