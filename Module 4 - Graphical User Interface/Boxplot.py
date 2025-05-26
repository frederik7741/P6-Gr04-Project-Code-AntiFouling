import matplotlib.pyplot as plt
import seaborn as sns

sus_scores = [
    92.5, 72.5, 85, 80, 80, 95, 85, 85, 77.5, 90,
    82.5, 80, 70, 90, 92.5, 57.5, 87.5, 87.5, 90, 85
]

plt.figure(figsize=(6, 8))
sns.boxplot(y=sus_scores, color='skyblue', linewidth=2.5)  


plt.title('Boxplot of SUS Scores', fontsize=14)
plt.ylabel('SUS Score', fontsize=12)
plt.grid(True, axis='y', linewidth=1.2)

plt.tight_layout()
plt.show()
