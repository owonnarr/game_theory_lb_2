import pandas as pd

def load_matrix(file_path):
    df = pd.read_excel(file_path, header=None)
    matrix = df.iloc[:-1, 1:].values.tolist()
    probabilities = df.iloc[-1, 1:].tolist()
    return matrix, probabilities

def validate_probabilities(probabilities):
    return round(sum(probabilities), 5) <= 1.0
