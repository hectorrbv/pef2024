import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Leer los datasets con manejo de valores faltantes
df1 = pd.read_csv('INTGSTMXM193N.csv', 
                  parse_dates=['observation_date'],
                  na_values=['.', 'NA', ''])  # Especificar valores que deben tratarse como NA
df1 = df1.rename(columns={'observation_date': 'DATE'})

df2 = pd.read_csv('DEXMXUS.csv', 
                  parse_dates=['DATE'],
                  na_values=['.', 'NA', ''])

# Merge los datasets
merged_df = pd.merge(df1, df2, on='DATE', how='inner')

# Eliminar filas con valores faltantes
merged_df = merged_df.dropna()

# Asegurarse de que las columnas sean numéricas
merged_df['INTGSTMXM193N'] = pd.to_numeric(merged_df['INTGSTMXM193N'], errors='coerce')
merged_df['DEXMXUS'] = pd.to_numeric(merged_df['DEXMXUS'], errors='coerce')

# Eliminar cualquier fila con valores no numéricos
merged_df = merged_df.dropna()

# Calcular correlación
correlation = merged_df['INTGSTMXM193N'].corr(merged_df['DEXMXUS'])

# Crear scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(merged_df['INTGSTMXM193N'], merged_df['DEXMXUS'], alpha=0.7)
plt.title(f'Scatter Plot: Interest Rates vs Exchange Rates\nCorrelation: {correlation:.4f}')
plt.xlabel('Interest Rates (INTGSTMXM193N)')
plt.ylabel('Exchange Rates (DEXMXUS)')
plt.tight_layout()
plt.savefig('correlation_plot.png')

# Crear heatmap de correlación
plt.figure(figsize=(8, 6))
correlation_matrix = merged_df[['INTGSTMXM193N', 'DEXMXUS']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('correlation_heatmap.png')

# Imprimir información detallada
print("\nCorrelation Analysis Results:")
print(f"Pearson Correlation Coefficient: {correlation:.4f}")
print("\nDescriptive Statistics:")
print(merged_df[['INTGSTMXM193N', 'DEXMXUS']].describe())

# Series de tiempo
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(merged_df['DATE'], merged_df['INTGSTMXM193N'], label='Interest Rates')
plt.title('Interest Rates Over Time')
plt.xlabel('Date')
plt.ylabel('Interest Rates')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(merged_df['DATE'], merged_df['DEXMXUS'], label='Exchange Rates', color='orange')
plt.title('Exchange Rates Over Time')
plt.xlabel('Date')
plt.ylabel('Exchange Rates')
plt.legend()
plt.tight_layout()
plt.savefig('time_series_plot.png')
