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

# 3. Histograms of Scaled Log Returns (X_scaled)
for i, asset in enumerate(X_scaled.columns):
    axes[2, 0].hist(X_scaled[asset], bins=20, color=["skyblue", "lightgreen", "salmon"][i], alpha=0.7, label=asset)

axes[2, 0].set_title("Histograms of Scaled Log Returns (X_scaled)")
axes[2, 0].set_xlabel("Scaled Log Returns")
axes[2, 0].set_ylabel("Frequency")
axes[2, 0].legend()

# -----------------
# y_scaled Visualizations
# -----------------

# 3. Histograms of Scaled Log Returns (y_scaled)
for i, asset in enumerate(y_scaled.columns):
    axes[2, 1].hist(y_scaled[asset], bins=20, color=["skyblue", "lightgreen", "salmon"][i], alpha=0.7, label=asset)

axes[2, 1].set_title("Histograms of Scaled Log Returns (y_scaled)")
axes[2, 1].set_xlabel("Scaled Log Returns")
axes[2, 1].set_ylabel("Frequency")
axes[2, 1].legend()

# Show all plots
plt.show()

# --------------------------------------------------------

# Set Seaborn style
sns.set(style="whitegrid", palette="muted", font_scale=1.2)

# -----------------
# Create subplots for visualizations
fig, axes = plt.subplots(6, 1, figsize=(18, 36))  # Single column for combined plots
fig.tight_layout(pad=6.0)  # Add spacing between plots

# -----------------
# Combined Visualizations
# -----------------

# 1. Line Plot of X_scaled and y_scaled (Log Returns Over Time)
for asset in X_scaled.columns:
    axes[0].plot(X_scaled.index, X_scaled[asset], label=f"X_scaled - {asset}", linestyle="-")
    axes[0].plot(y_scaled.index, y_scaled[asset], label=f"y_scaled - {asset}", linestyle="--")

axes[0].set_title("Line Plot of Scaled Log Returns Over Time (X_scaled and y_scaled)")
axes[0].set_xlabel("Date")
axes[0].set_ylabel("Scaled Log Returns")
axes[0].legend(title="Assets")
axes[0].grid(True)

# 2. Boxplot of Scaled Log Returns
sns.boxplot(data=X_scaled, ax=axes[1], palette="Set2", width=0.4, position=0, showmeans=True, showmeans=True,)

sns.boxplot(data=y_scaled, ax=axes[1], palette="Set3",)

plt.tight_layout()
