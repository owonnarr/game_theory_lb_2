from datetime import datetime
import pandas as pd
import numpy as np

def remove_duplicate_strategies(matrix, row_labels, results):
    unique_matrix, unique_indices = np.unique(matrix, axis=0, return_index=True)
    removed_duplicates = len(matrix) - len(unique_matrix)
    matrix = unique_matrix
    row_labels = [row_labels[i] for i in sorted(unique_indices)]
    if removed_duplicates > 0:
        results += f"Видалено {removed_duplicates} дублюючих стратегій. Залишилось: {len(matrix)}\n"

    to_remove = set()
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j and all(matrix[i] <= matrix[j]) and any(matrix[i] < matrix[j]):
                to_remove.add(i)
    if to_remove:
        results += f"Видалено {len(to_remove)} домінуючих стратегій: {[row_labels[i] for i in to_remove]}\n"
        matrix = np.delete(matrix, list(to_remove), axis=0)
        row_labels = [label for idx, label in enumerate(row_labels) if idx not in to_remove]

    return results, matrix, row_labels

def calculate_all_criteria(matrix, probabilities, selected_criteria, lambdas, row_labels, col_labels):
    matrix = np.array(matrix)
    results = ""
    optimal = {}
    criteria_matrices = {}

    results, matrix, row_labels = remove_duplicate_strategies(matrix, row_labels, results)

    if selected_criteria.get("bayes"):
        bayes = np.dot(matrix, probabilities)
        max_val = max(bayes)
        idx = list(bayes).index(max_val)
        results += f"\nКритерій Бейєса: оптимальна стратегія: {row_labels[idx]}\n"
        optimal["Бейєса"] = row_labels[idx]
        criteria_matrices["Бейєса"] = bayes

    if selected_criteria.get("wald"):
        wald = matrix.min(axis=1)
        max_val = max(wald)
        idx = list(wald).index(max_val)
        results += f"Критерій Вальда: оптимальна стратегія: {row_labels[idx]}\n"
        optimal["Вальда"] = row_labels[idx]
        criteria_matrices["Вальда"] = wald

    if selected_criteria.get("savage"):
        regret = matrix.max(axis=0) - matrix
        savage = regret.max(axis=1)
        min_val = min(savage)
        idx = list(savage).index(min_val)
        results += f"Критерій Севіджа: оптимальна стратегія: {row_labels[idx]}\n"
        optimal["Севіджа"] = row_labels[idx]
        criteria_matrices["Севіджа"] = savage

    if selected_criteria.get("variation"):
        mean = matrix.mean(axis=1)
        std_dev = matrix.std(axis=1)
        coef = std_dev / (mean + 1e-9)
        min_val = min(coef)
        idx = list(coef).index(min_val)
        results += f"Коефіцієнти варіації: оптимальна стратегія: {row_labels[idx]}\n"
        optimal["Варіація"] = row_labels[idx]
        criteria_matrices["Варіація"] = coef

    if selected_criteria.get("hurwicz"):
        for lambd in lambdas:
            min_vals = matrix.min(axis=1)
            max_vals = matrix.max(axis=1)
            hurwicz = lambd * max_vals + (1 - lambd) * min_vals
            max_val = max(hurwicz)
            idx = list(hurwicz).index(max_val)
            results += f"Критерій Гурвіца λ={lambd}: {hurwicz}, оптимальна стратегія: {row_labels[idx]}\n"
            optimal[f"Гурвіц λ={lambd}"] = row_labels[idx]
            criteria_matrices[f"Гурвіц λ={lambd}"] = hurwicz

    results = set_top_and_min_price_game(matrix, results, row_labels, col_labels)

    return results, optimal, criteria_matrices

def set_top_and_min_price_game(matrix, results, row_labels, col_labels):
    min_row_max = matrix.min(axis=1)
    max_min_val = max(min_row_max)
    min_row_index = list(min_row_max).index(max_min_val)

    max_col_min = matrix.max(axis=0)
    min_max_val = min(max_col_min)
    max_col_index = list(max_col_min).index(min_max_val)

    results += f"\nНижня ціна гри (max min): {max_min_val}, стратегія: {row_labels[min_row_index]}\n"
    results += f"\nВерхня ціна гри (min max): {min_max_val}, стратегія: {col_labels[max_col_index]}\n"

    if np.isclose(max_min_val, min_max_val):
        results += f"Оптимальна чиста стратегія існує: гравець 1 - {row_labels[min_row_index]}, гравець 2 - {col_labels[max_col_index]}\n"
    else:
        results += "Оптимальної чистої стратегії не знайдено\n"

    return results

def save_results(optimal_dict):
    with pd.ExcelWriter("results/calculated_" + datetime.now().isoformat() + ".xlsx") as writer:
        optimal_df = pd.DataFrame(optimal_dict.items(), columns=["Критерій", "Оптимальна стратегія"])
        optimal_df.to_excel(writer, sheet_name="Оптимальні стратегії", index=False)