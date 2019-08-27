import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

fields = ['fast_switch', 'q_learning_epsilon']
df = pd.read_csv('penalty_results.csv')
sns.set_style('whitegrid')
df[:1000].plot(x='time', y=fields, figsize=(10, 5), grid=True)
plt.show()
