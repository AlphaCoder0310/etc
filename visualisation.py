import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set(style="whitegrid", palette="muted", font_scale=1.2)

# -----------------
# Dynamically calculate the number of rows needed for subplots based on the columns
n_X = len(X_scaled.columns)  # Number of columns in X_scaled
n_y = len(y_scaled.columns)  # Number of columns in y_scaled

# Create subplots for individual visualizations
# Adjust rows dynamically based on the size of the data
n_rows = max(n_X, n_y)  # Use the larger number of columns to determine rows
fig, axes = plt.subplots(n_rows, 2, figsize=(18, n_rows * 4))  # Dynamic rows, 2 columns
fig.tight_layout(pad=6.0)  # Add spacing between plots

# -----------------
# X_scaled Visualizations
# -----------------

# 1. Line Plot of X_scaled (Log Returns Over Time)
for i, asset in enumerate(X_scaled.columns):
    axes[i, 0].plot(X_scaled.index, X_scaled[asset], label=asset)
    axes[i, 0].set_title(f"Line Plot of Scaled Log Returns for {asset} (X_scaled)")
    axes[i, 0].set_xlabel("Date")
    axes[i, 0].set_ylabel("Scaled Log Returns")
    axes[i, 0].legend(title="Assets")
    axes[i, 0].grid(True)

# 2. Boxplot of Scaled Log Returns (X_scaled)
sns.boxplot(data=X_scaled, ax=axes[0, 1], palette="Set3")
axes[0, 1].set_title("Boxplot of Scaled Log Returns (X_scaled)")
axes[0, 1].set_xlabel("Assets")
axes[0, 1].set_ylabel("Scaled Log Returns")

# 3. Histograms of Scaled Log Returns (X_scaled)
for i, asset in enumerate(X_scaled.columns):
    axes[i, 1].hist(X_scaled[asset], bins=20, alpha=0.7, label=asset)
    axes[i, 1].set_title(f"Histogram of Scaled Log Returns for {asset} (X_scaled)")
    axes[i, 1].set_xlabel("Scaled Log Returns")
    axes[i, 1].set_ylabel("Frequency")
    axes[i, 1].legend()

# -----------------
# y_scaled Visualizations
# -----------------

# 1. Line Plot of y_scaled (Log Returns Over Time)
for i, asset in enumerate(y_scaled.columns):
    axes[i, 0].plot(y_scaled.index, y_scaled[asset], label=asset, linestyle="--")
    axes[i, 0].set_title(f"Line Plot of Scaled Log Returns for {asset} (y_scaled)")
    axes[i, 0].set_xlabel("Date")
    axes[i, 0].set_ylabel("Scaled Log Returns")
    axes[i, 0].legend(title="Assets")
    axes[i, 0].grid(True)

# 2. Boxplot of Scaled Log Returns (y_scaled)
sns.boxplot(data=y_scaled, ax=axes[0, 1], palette="Set2")
axes[0, 1].set_title("Boxplot of Scaled Log Returns (y_scaled)")
axes[0, 1].set_xlabel("Assets")
axes[0, 1].set_ylabel("Scaled Log Returns")

# 3. Histograms of Scaled Log Returns (y_scaled)
for i, asset in enumerate(y_scaled.columns):
    axes[i, 1].hist(y_scaled[asset], bins=20, alpha=0.7, label=asset)
    axes[i, 1].set_title(f"Histogram of Scaled Log Returns for {asset} (y_scaled)")
    axes[i, 1].set_xlabel("Scaled Log Returns")
    axes[i, 1].set_ylabel("Frequency")
    axes[i, 1].legend()

# -----------------
# Combined Visualizations
# -----------------

# Dynamically create subplots for combined visualizations
fig_combined, axes_combined = plt.subplots(2, 1, figsize=(18, 12))  # Fixed 2 rows, 1 column
fig_combined.tight_layout(pad=6.0)

# 1. Line Plot of X_scaled and y_scaled (Log Returns Over Time)
for asset in X_scaled.columns:
    if asset in y_scaled.columns:  # Ensure overlap between X_scaled and y_scaled columns
        axes_combined[0].plot(X_scaled.index, X_scaled[asset], label=f"X_scaled - {asset}", linestyle="-")
        axes_combined[0].plot(y_scaled.index, y_scaled[asset], label=f"y_scaled - {asset}", linestyle="--")

axes_combined[0].set_title("Line Plot of Scaled Log Returns Over Time (X_scaled and y_scaled)")
axes_combined[0].set_xlabel("Date")
axes_combined[0].set_ylabel("Scaled Log Returns")
axes_combined[0].legend(title="Assets")
axes_combined[0].grid(True)

# 2. Boxplot of Scaled Log Returns (Combined for X_scaled and y_scaled)
combined_data = X_scaled.join(y_scaled, how="outer", rsuffix="_y")  # Combine both datasets
sns.boxplot(data=combined_data, ax=axes_combined[1], palette="Set3")
axes_combined[1].set_title("Combined Boxplot of Sc
