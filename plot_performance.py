import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# fields = ['q_learning', 'manual']
df = pd.read_csv('penalty_results.csv')
sns.set_style("whitegrid")
df[:1000].plot(x='time', y=['manual', 'q_learning', 'q_learning_epsilon'], figsize=(10, 5), grid=True)

plt.show()
