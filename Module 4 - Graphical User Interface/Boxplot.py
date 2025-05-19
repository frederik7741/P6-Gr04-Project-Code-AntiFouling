import matplotlib.pyplot as plt
import seaborn as sns

# SUS Scores
sus_scores = [
    92.5, 72.5, 85, 80, 80, 95, 85, 85, 77.5, 90,
    82.5, 80, 70, 90, 92.5, 57.5, 87.5, 87.5, 90, 85
]

# Create a boxplot with thicker lines
plt.figure(figsize=(6, 8))
sns.boxplot(y=sus_scores, color='skyblue', linewidth=2.5)  # Thicker lines here

# Labels and title
plt.title('Boxplot of SUS Scores', fontsize=14)
plt.ylabel('SUS Score', fontsize=12)
plt.grid(True, axis='y', linewidth=1.2)

# Show plot
plt.tight_layout()
plt.show()
