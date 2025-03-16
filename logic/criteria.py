from datetime import datetime

import pandas as pd
import numpy as np

def calculate_all_criteria(matrix, probabilities, selected_criteria, lambdas):
    matrix = np.array(matrix)
    results = ""
    optimal = {}
    criteria_matrices = {}

    if selected_criteria.get("bayes"):
        bayes = np.dot(matrix, probabilities)
        max_val = max(bayes)
        idx = list(bayes).index(max_val)
        results += f"Критерій Бейєса: оптимальна стратегія: S{idx + 1}\n"
        optimal["Бейєса"] = f"S{idx + 1}"
        criteria_matrices["Бейєса"] = bayes

    if selected_criteria.get("wald"):
        wald = matrix.min(axis=1)
        max_val = max(wald)
        idx = list(wald).index(max_val)
        results += f"Критерій Вальда: оптимальна стратегія: S{idx + 1}\n"
        optimal["Вальда"] = f"S{idx + 1}"
        criteria_matrices["Вальда"] = wald

    if selected_criteria.get("savage"):
        regret = matrix.max(axis=0) - matrix
        savage = regret.max(axis=1)
        min_val = min(savage)
        idx = list(savage).index(min_val)
        results += f"Критерій Севіджа: оптимальна стратегія: S{idx + 1}\n"
        optimal["Севіджа"] = f"S{idx + 1}"
        criteria_matrices["Севіджа"] = savage

    if selected_criteria.get("variation"):
        mean = matrix.mean(axis=1)
        std_dev = matrix.std(axis=1)
        coef = std_dev / (mean + 1e-9)
        min_val = min(coef)
        idx = list(coef).index(min_val)
        results += f"Коефіцієнти варіації: оптимальна стратегія: S{idx + 1}\n"
        optimal["Варіація"] = f"S{idx + 1}"
        criteria_matrices["Варіація"] = coef

    if selected_criteria.get("hurwicz"):
        for lambd in lambdas:
            min_vals = matrix.min(axis=1)
            max_vals = matrix.max(axis=1)
            hurwicz = lambd * max_vals + (1 - lambd) * min_vals
            max_val = max(hurwicz)
            idx = list(hurwicz).index(max_val)
            results += f"Критерій Гурвіца λ={lambd}: {hurwicz}, оптимальна стратегія: S{idx + 1}\n"
            optimal[f"Гурвіц λ={lambd}"] = f"S{idx + 1}"
            criteria_matrices[f"Гурвіц λ={lambd}"] = hurwicz

    return results, optimal, criteria_matrices

def save_results(optimal_dict):
    with pd.ExcelWriter("results/calculated_" + datetime.now().isoformat() + ".xlsx") as writer:

        optimal_df = pd.DataFrame(optimal_dict.items(), columns=["Критерій", "Оптимальна стратегія"])
        optimal_df.to_excel(writer, sheet_name="Оптимальні стратегії", index=False)