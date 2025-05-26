import matplotlib.pyplot as plt

participants = list(range(1, 21))

cumulative_avg = [
    92.5, 82.5, 83.33333333, 82.5, 82, 84.16666667, 84.28571429, 84.375,
    83.61111111, 84.25, 84.09090909, 83.75, 82.69230769, 83.21428571,
    83.83333333, 82.1875, 82.5, 82.77777778, 83.15789474, 83.25
]

plt.figure(figsize=(10, 6))
plt.plot(participants, cumulative_avg, linestyle='-', color='blue')

plt.title('Cumulative Average Plot')
plt.xlabel('Test Participants')
plt.ylabel('Cumulative Average')
plt.grid(True)
plt.xticks(participants)

min_y = int(min(cumulative_avg)) - 1
max_y = int(max(cumulative_avg)) + 1
plt.yticks(range(min_y, max_y + 1, 1))

plt.tight_layout()
plt.show()
