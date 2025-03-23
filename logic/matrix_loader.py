import pandas as pd

def load_matrix(file_path):
    df = pd.read_excel(file_path, header=None)

    matrix = df.iloc[:-1, 1:].values.tolist()
    probabilities = df.iloc[-1, 1:].tolist()

    row_labels = df.iloc[:-1, 0].tolist()
    col_labels = df.iloc[0, 1:].tolist()

    return matrix, probabilities, row_labels, col_labels

def validate_probabilities(probabilities):
    return round(sum(probabilities), 5) <= 1.0
