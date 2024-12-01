import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Month mapping
month_map = {
    'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 
    'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
}

# Process inflation data
inflation_data = pd.read_csv('INFLACION.csv', header=None, names=['date', 'inflation'])
inflation_data['date'] = inflation_data['date'].apply(lambda x: f"{x.split()[1]}-{month_map[x.split()[0]]}-01")
inflation_data['date'] = pd.to_datetime(inflation_data['date'])

# Process exchange rate data
exchange_data = pd.read_csv('DEXMXUS.csv')
exchange_data['DATE'] = pd.to_datetime(exchange_data['DATE'])
# Clean exchange rate data
exchange_data['DEXMXUS'] = pd.to_numeric(exchange_data['DEXMXUS'].str.replace("'", ""), errors='coerce')
exchange_data = exchange_data.rename(columns={'DATE': 'date', 'DEXMXUS': 'exchange_rate'})

# Merge and analyze
merged_data = pd.merge(inflation_data, exchange_data, on='date', how='inner')
merged_data = merged_data.dropna()

correlation = merged_data['inflation'].corr(merged_data['exchange_rate'])
print(f"Correlation coefficient: {correlation:.3f}")

# Plotting
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_data, x='exchange_rate', y='inflation')
plt.title(f'Inflation vs Exchange Rate (Correlation: {correlation:.3f})')
plt.xlabel('Exchange Rate (MXN/USD)')
plt.ylabel('Inflation Rate (%)')
plt.show()
