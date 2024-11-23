import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Example data (replace this with your actual X_scaled and y_scaled DataFrames)
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=100)  # Example date range
assets = ['Asset1', 'Asset2', 'Asset3']

# Example scaled data
X_scaled = pd.DataFrame(np.random.randn(100, 3), index=dates, columns=assets)
y_scaled = pd.DataFrame(np.random.randn(100, 3), index=dates, columns=assets)

# Set Seaborn style
sns.set(style="whitegrid", palette="muted", font_scale=1.2)

# -----------------
# Create subplots for multiple visualizations for X_scaled and y_scaled
fig, axes = plt.subplots(6, 2, figsize=(18, 24))
fig.tight_layout(pad=6.0)  # Add spacing between plots

# -----------------
# X_scaled Visualizations
# -----------------

# 1. Line Plot of X_scaled (Log Returns Over Time)
for asset in X_scaled.columns:
    axes[0, 0].plot(X_scaled.index, X_scaled[asset], label=asset)

axes[0, 0].set_title("Line Plot of Scaled Log Returns Over Time (X_scaled)")
axes[0, 0].set_xlabel("Date")
axes[0, 0].set_ylabel("Scaled Log Returns")
axes[0, 0].legend(title="Assets")
axes[0, 0].grid(True)

# 2. Boxplot of Scaled Log Returns (X_scaled)
sns.boxplot(data=X_scaled, ax=axes[1, 0], palette="Set3")
axes[1, 0].set_title("Boxplot of Scaled Log Returns (X_scaled)")
axes[1, 0].set_xlabel("Assets")
axes[1, 0].set_ylabel("Scaled Log Returns")

# 3. Histogram of Scaled Log Returns (X_scaled)
X_scaled.hist(bins=20, ax=axes[2, 0], color=["skyblue", "lightgreen", "salmon"], layout=(1, 3))
axes[2, 0].set_title("Histograms of Scaled Log Returns (X_scaled)")

# 4. KDE Plot of Scaled Log Returns (X_scaled)
for asset in X_scaled.columns:
    sns.kdeplot(X_scaled[asset], ax=axes[3, 0], label=asset, fill=True, alpha=0.4)

axes[3, 0].set_title("KDE Plot of Scaled Log Returns (X_scaled)")
axes[3, 0].set_xlabel("Scaled Log Returns")
axes[3, 0].set_ylabel("Density")
axes[3, 0].legend(title="Assets")

# 5. Scatterplot of Two Specific Assets (X_scaled)
sns.scatterplot(x=X_scaled['Asset1'], y=X_scaled['Asset2'], ax=axes[4, 0], color="blue", alpha=0.7)
axes[4, 0].set_title("Scatterplot of Scaled Log Returns (Asset1 vs Asset2) (X_scaled)")
axes[4, 0].set_xlabel("Asset1 Scaled Log Returns")
axes[4, 0].set_ylabel("Asset2 Scaled Log Returns")
axes[4, 0].grid(True)

# 6. Correlation Matrix Heatmap (X_scaled)
corr_matrix = X_scaled.corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1, ax=axes[5, 0])
axes[5, 0].set_title("Correlation Matrix of Scaled Log Returns (X_scaled)")

# -----------------
# y_scaled Visualizations
# -----------------

# 1. Line Plot of y_scaled (Log Returns Over Time)
for asset in y_scaled.columns:
    axes[0, 1].plot(y_scaled.index, y_scaled[asset], label=asset)

axes[0, 1].set_title("Line Plot of Scaled Log Returns Over Time (y_scaled)")
axes[0, 1].set_xlabel("Date")
axes[0, 1].set_ylabel("Scaled Log Returns")
axes[0, 1].legend(title="Assets")
axes[0, 1].grid(True)

# 2. Boxplot of Scaled Log Returns (y_scaled)
sns.boxplot(data=y_scaled, ax=axes[1, 1], palette="Set3")
axes[1, 1].set_title("Boxplot of Scaled Log Returns (y_scaled)")
axes[1, 1].set_xlabel("Assets")
axes[1, 1].set_ylabel("Scaled Log Returns")

# 3. Histogram of Scaled Log Returns (y_scaled)
y_scaled.hist(bins=20, ax=axes[2, 1], color=["skyblue", "lightgreen", "salmon"], layout=(1, 3))
axes[2, 1].set_title("Histograms of Scaled Log Returns (y_scaled)")

# 4. KDE Plot of Scaled Log Returns (y_scaled)
for asset in y_scaled.columns:
    sns.kdeplot(y_scaled[asset], ax=axes[3, 1], label=asset, fill=True, alpha=0.4)

axes[3, 1].set_title("KDE Plot of Scaled Log Returns (y_scaled)")
axes[3, 1].set_xlabel("Scaled Log Returns")
axes[3, 1].set_ylabel("Density")
axes[3, 1].legend(title="Assets")

# 5. Scatterplot of Two Specific Assets (y_scaled)
sns.scatterplot(x=y_scaled['Asset1'], y=y_scaled['Asset2'], ax=axes[4, 1], color="blue", alpha=0.7)
axes[4, 1].set_title("Scatterplot of Scaled Log Returns (Asset1 vs Asset2) (y_scaled)")
axes[4, 1].set_xlabel("Asset1 Scaled Log Returns")
axes[4, 1].set_ylabel("Asset2 Scaled Log Returns")
axes[4, 1].grid(True)

# 6. Correlation Matrix Heatmap (y_scaled)
corr_matrix_y = y_scaled.corr()
sns.heatmap(corr_matrix_y, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1, ax=axes[5, 1])
axes[5, 1].set_title("Correlation Matrix of Scaled Log Returns (y_scaled)")

# Show all plots
plt.show()
