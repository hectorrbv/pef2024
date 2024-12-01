import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class EconomicCycleAnalyzer:
    def __init__(self):
        self.criteria = {
            'exchange_rate': {
                'Recovery': {'min': None, 'max': 19.0},
                'Normal': {'min': 19.0, 'max': 20.5},
                'Recession': {'min': 20.5, 'max': None}
            },
            'inflation': {
                'Recovery': {'min': None, 'max': 4.0},
                'Normal': {'min': 4.0, 'max': 6.0},
                'Recession': {'min': 6.0, 'max': None}
            },
            'debt': {
                'Recovery': {'min': None, 'max': 52.0},
                'Normal': {'min': 52.0, 'max': 55.0},
                'Recession': {'min': 55.0, 'max': None}
            }
        }
        self.transition_matrix = None
        self.weights = {
            'exchange_rate': 0.4,
            'inflation': 0.35,
            'debt': 0.25
        }
    
    def load_and_merge_data(self, exchange_rate_file, inflation_file, debt_file):
        """
        Carga y combina los datos de diferentes fuentes
        """
        exchange_rate = pd.read_csv(exchange_rate_file, parse_dates=['DATE'])
        inflation = pd.read_csv(inflation_file, parse_dates=['observation_date'])
        debt = pd.read_csv(debt_file, parse_dates=['observation_date'])
        
        exchange_rate = exchange_rate.rename(columns={'DATE': 'date', 'DEXMXUS': 'exchange_rate'})
        inflation = inflation.rename(columns={'observation_date': 'date', 'FPCPITOTLZGMEX': 'inflation'})
        debt = debt.rename(columns={'observation_date': 'date', 'GGGDTAMXA188N': 'debt'})
        
        exchange_rate['exchange_rate'] = pd.to_numeric(exchange_rate['exchange_rate'], errors='coerce')
        inflation['inflation'] = pd.to_numeric(inflation['inflation'], errors='coerce')
        debt['debt'] = pd.to_numeric(debt['debt'], errors='coerce')
        
        data = pd.merge(exchange_rate, inflation, on='date', how='outer')
        data = pd.merge(data, debt, on='date', how='outer')
        
        return data.sort_values('date')
    
    def classify_single_indicator(self, value, criteria):
        """
        Clasifica un valor individual según los criterios establecidos
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            return np.nan
            
        if pd.isna(value):
            return np.nan
        
        if value <= criteria['Recovery']['max']:
            return 'Recovery'
        elif value > criteria['Recession']['min']:
            return 'Recession'
        else:
            return 'Normal'
    
    def calculate_composite_state(self, row):
        """
        Calcula el estado compuesto basado en múltiples indicadores
        """
        states = {
            'Recovery': 1,
            'Normal': 2,
            'Recession': 3
        }
        
        indicator_states = {}
        for indicator in ['exchange_rate', 'inflation', 'debt']:
            try:
                value = float(row[indicator])
                indicator_states[indicator] = self.classify_single_indicator(
                    value, self.criteria[indicator]
                )
            except (ValueError, TypeError):
                indicator_states[indicator] = np.nan
        
        weighted_score = 0
        valid_weights = 0
        
        for indicator, state in indicator_states.items():
            if pd.notna(state):
                weighted_score += states[state] * self.weights[indicator]
                valid_weights += self.weights[indicator]
        
        if valid_weights == 0:
            return np.nan
            
        final_score = weighted_score / valid_weights
        
        if final_score <= 1.67:
            return 'Recovery'
        elif final_score <= 2.33:
            return 'Normal'
        else:
            return 'Recession'
    
    def analyze_historical_data(self, data):
        """
        Analiza los datos históricos y calcula el estado compuesto
        """
        df = data.copy()
        
        for indicator in ['exchange_rate', 'inflation', 'debt']:
            if indicator in df.columns:
                df[indicator] = pd.to_numeric(df[indicator], errors='coerce')
        
        df['composite_state'] = df.apply(self.calculate_composite_state, axis=1)
        
        # Calcular matriz de transición
        self.transition_matrix = self.calculate_transition_matrix(df['composite_state'].dropna())
        
        return df
    
    def calculate_transition_matrix(self, states):
        """
        Calcula las probabilidades de transición entre estados
        """
        unique_states = sorted(states.unique())
        n_states = len(unique_states)
        trans_matrix = pd.DataFrame(
            np.zeros((n_states, n_states)),
            index=unique_states,
            columns=unique_states
        )
        
        for i in range(len(states)-1):
            current_state = states.iloc[i]
            next_state = states.iloc[i+1]
            trans_matrix.loc[current_state, next_state] += 1
            
        return trans_matrix.div(trans_matrix.sum(axis=1), axis=0)
    
    def predict_future_states(self, current_state, n_periods=12, seed=42):
        """
        Predice estados futuros usando cadenas de Markov
        """
        if self.transition_matrix is None:
            raise ValueError("Debe ejecutar analyze_historical_data primero")
            
        np.random.seed(seed)
        states = []
        
        for _ in range(n_periods):
            states.append(current_state)
            probs = self.transition_matrix.loc[current_state]
            current_state = np.random.choice(probs.index, p=probs.values)
            
        return pd.Series(states, name='predicted_state')
    
    def plot_combined_analysis(self, historical_data, future_states):
        """
        Visualiza el análisis histórico y la predicción en un solo gráfico
        """
        plt.figure(figsize=(15, 6))
        
        # Datos históricos
        historical = historical_data[['date', 'composite_state']].dropna()
        plt.scatter(historical['date'], historical['composite_state'], 
                   label='Datos Históricos', alpha=0.6)
        
        # Predicciones
        last_date = historical['date'].max()
        future_dates = pd.date_range(start=last_date, periods=len(future_states)+1, freq='M')[1:]
        plt.scatter(future_dates, future_states, label='Predicción', alpha=0.6)
        
        plt.title('Análisis Económico y Predicción')
        plt.xlabel('Fecha')
        plt.ylabel('Estado Económico')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        # Imprimir resumen de predicción
        print("\n=== RESUMEN DE PREDICCIÓN ===")
        state_counts = future_states.value_counts()
        total_periods = len(future_states)
        
        print(f"\nPredicción para los próximos {total_periods} meses:")
        for state in ['Recovery', 'Normal', 'Recession']:
            if state in state_counts:
                count = state_counts[state]
                percentage = (count / total_periods) * 100
                print(f"{state}: {count} meses ({percentage:.1f}%)")
        
        # Imprimir matriz de transición
        print("\n=== MATRIZ DE PROBABILIDADES DE TRANSICIÓN ===")
        print(self.transition_matrix.round(3))

def main():
    analyzer = EconomicCycleAnalyzer()
    
    data = analyzer.load_and_merge_data(
        'DEXMXUS.csv',
        'INFLACION.csv',
        'DEUDA.csv'
    )
    
    analyzed_data = analyzer.analyze_historical_data(data)
    
    # Obtener el último estado conocido
    last_state = analyzed_data['composite_state'].dropna().iloc[-1]
    
    # Predecir estados futuros
    future_states = analyzer.predict_future_states(last_state)
    
    # Visualizar resultados
    analyzer.plot_combined_analysis(analyzed_data, future_states)

if __name__ == "__main__":
    main()
