import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Example data (replace this with your actual X_scaled and y_scaled DataFrames)
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=100)  # Example date range
assets = ['Asset1', 'Asset2', 'Asset3']

# Example scaled data
X_scaled_df = pd.DataFrame(np.random.randn(100, 3), index=dates, columns=assets)
y_scaled_df = pd.DataFrame(np.random.randn(100, 3), index=dates, columns=assets)

# Set Seaborn style
sns.set(style="whitegrid", palette="muted", font_scale=1.2)

# -----------------
# Create subplots for multiple visualizations
fig, axes = plt.subplots(3, 2, figsize=(16, 18))
fig.tight_layout(pad=6.0)  # Add spacing between plots

# -----------------
# 1. Line Plot of X_scaled (Log Returns Over Time)
for asset in X_scaled_df.columns:
    axes[0, 0].plot(X_scaled_df.index, X_scaled_df[asset], label=asset)

axes[0, 0].set_title("Line Plot of Scaled Log Returns Over Time (X_scaled)")
axes[0, 0].set_xlabel("Date")
axes[0, 0].set_ylabel("Scaled Log Returns")
axes[0, 0].legend(title="Assets")
axes[0, 0].grid(True)

# -----------------
# 2. Boxplot of Scaled Log Returns (X_scaled)
sns.boxplot(data=X_scaled_df, ax=axes[0, 1], palette="Set3")
axes[0, 1].set_title("Boxplot of Scaled Log Returns (X_scaled)")
axes[0, 1].set_xlabel("Assets")
axes[0, 1].set_ylabel("Scaled Log Returns")

# -----------------
# 3. Histogram of Scaled Log Returns (X_scaled)
X_scaled_df.hist(bins=20, ax=axes[1, 0], color=["skyblue", "lightgreen", "salmon"], layout=(1, 3))
axes[1, 0].set_title("Histograms of Scaled Log Returns (X_scaled)")

# -----------------
# 4. KDE Plot of Scaled Log Returns (X_scaled)
for asset in X_scaled_df.columns:
    sns.kdeplot(X_scaled_df[asset], ax=axes[1, 1], label=asset, fill=True, alpha=0.4)

axes[1, 1].set_title("KDE Plot of Scaled Log Returns (X_scaled)")
axes[1, 1].set_xlabel("Scaled Log Returns")
axes[1, 1].set_ylabel("Density")
axes[1, 1].legend(title="Assets")

# -----------------
# 5. Scatterplot of Two Specific Assets (X_scaled)
sns.scatterplot(x=X_scaled_df['Asset1'], y=X_scaled_df['Asset2'], ax=axes[2, 0], color="blue", alpha=0.7)
axes[2, 0].set_title("Scatterplot of Scaled Log Returns (Asset1 vs Asset2)")
axes[2, 0].set_xlabel("Asset1 Scaled Log Returns")
axes[2, 0].set_ylabel("Asset2 Scaled Log Returns")
axes[2, 0].grid(True)

# -----------------
# 6. Correlation Matrix Heatmap (X_scaled)
corr_matrix = X_scaled_df.corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1, ax=axes[2, 1])
axes[2, 1].set_title("Correlation Matrix of Scaled Log Returns (X_scaled)")

# Show all plots
plt.show()
