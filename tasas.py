import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo CSV
df = pd.read_csv('INTGSTMXM193N.csv', parse_dates=['observation_date'])

# Configurar el gráfico
plt.figure(figsize=(12, 6))
plt.plot(df['observation_date'], df['INTGSTMXM193N'], marker='o')
plt.title('Tendencia de Tasas a lo Largo del Tiempo', fontsize=15)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Valor', fontsize=12)
plt.grid(True)
plt.xticks(rotation=45)

# Resaltar puntos de cambio significativos
plt.annotate('Caída en 2020', 
             xy=(pd.Timestamp('2020-04-01'), 6.09), 
             xytext=(10, 30), 
             textcoords='offset points', 
             arrowprops=dict(arrowstyle='->'))

plt.annotate('Pico máximo', 
             xy=(pd.Timestamp('2023-03-01'), 11.23), 
             xytext=(10, -30), 
             textcoords='offset points', 
             arrowprops=dict(arrowstyle='->'))

plt.tight_layout()
plt.show()
