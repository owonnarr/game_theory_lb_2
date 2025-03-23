from tkinter import *
from tkinter import filedialog, messagebox
from logic.matrix_loader import load_matrix, validate_probabilities
from logic.criteria import calculate_all_criteria, save_results
import os

class GameTheoryApp:
    def __init__(self, root):
        self.criteria_matrices = None
        self.root = root
        self.root.title("Інструмент з теорії ігор")
        self.file_path = None

        Label(root, text="Файл з матрицею:").grid(row=0, column=0, sticky=W)
        self.file_label = Label(root, text="Не обрано", fg="gray")
        self.file_label.grid(row=0, column=1, sticky=W)

        Button(root, text="Вибрати файл", command=self.select_file).grid(row=0, column=2)

        self.criteria_vars = {
            "bayes": BooleanVar(),
            "wald": BooleanVar(),
            "savage": BooleanVar(),
            "variation": BooleanVar(),
            "hurwicz": BooleanVar(),
        }

        Label(root, text="Оберіть критерії:").grid(row=1, column=0, sticky=W)
        Checkbutton(root, text="Бейєса", variable=self.criteria_vars["bayes"]).grid(row=2, column=0, sticky=W)
        Checkbutton(root, text="Вальда", variable=self.criteria_vars["wald"]).grid(row=3, column=0, sticky=W)
        Checkbutton(root, text="Севіджа", variable=self.criteria_vars["savage"]).grid(row=4, column=0, sticky=W)
        Checkbutton(root, text="Мін. коеф. варіації", variable=self.criteria_vars["variation"]).grid(row=5, column=0,
                                                                                                     sticky=W)
        Checkbutton(root, text="Гурвіца", variable=self.criteria_vars["hurwicz"]).grid(row=6, column=0, sticky=W)

        Label(root, text="λ для Гурвіца:").grid(row=7, column=0, sticky=W)
        self.lambda1_entry = Entry(root)
        self.lambda1_entry.insert(0, "0.5")
        self.lambda1_entry.grid(row=7, column=1)

        self.lambda2_entry = Entry(root)
        self.lambda2_entry.insert(0, "0.3")
        self.lambda2_entry.grid(row=7, column=2)

        self.result_text = Text(root, height=10, width=100)
        self.result_text.grid(row=8, column=0, columnspan=3)

        buttons_frame = Frame(root)
        buttons_frame.grid(row=9, column=0, columnspan=3, pady=10)

        Button(buttons_frame, text="Прорахувати", command=self.calculate, width=15).grid(row=0, column=0, padx=5)
        Button(buttons_frame, text="Зберегти", command=self.save, width=15).grid(row=0, column=1, padx=5)
        Button(buttons_frame, text="Скинути", command=self.reset, width=15).grid(row=0, column=2, padx=5)
        Button(buttons_frame, text="Вийти", command=self.root.quit, width=15).grid(row=0, column=3, padx=5)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if path:
            self.file_path = path
            self.file_label.config(text=os.path.basename(path), fg="black")

    def calculate(self):
        if not self.file_path:
            messagebox.showwarning("Увага", "Оберіть файл з матрицею!")
            return

        try:
            matrix, probabilities, row_labels, col_labels = load_matrix(self.file_path)
            if not validate_probabilities(probabilities):
                messagebox.showerror("Помилка", "Ймовірності не валідні (сума > 1)")
                return

            lambdas = [float(self.lambda1_entry.get()), float(self.lambda2_entry.get())]
            selected_criteria = {k: v.get() for k, v in self.criteria_vars.items()}
            results, optimal, criteria_matrices = calculate_all_criteria(matrix, probabilities, selected_criteria, lambdas, row_labels, col_labels)

            self.result_text.delete("1.0", END)
            self.result_text.insert(END, results)
            self.optimal_strategies = optimal
            self.criteria_matrices = criteria_matrices

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def save(self):
        if hasattr(self, "optimal_strategies") and hasattr(self, "criteria_matrices"):
            save_results(self.optimal_strategies, self.criteria_matrices)
            messagebox.showinfo("Успіх", "Результати збережено у results/calculated_current_date.xlsx")

    def reset(self):
        for var in self.criteria_vars.values():
            var.set(False)

        self.lambda1_entry.delete(0, END)
        self.lambda1_entry.insert(0, "0.5")
        self.lambda2_entry.delete(0, END)
        self.lambda2_entry.insert(0, "0.3")

        self.result_text.delete("1.0", END)

        self.file_path = None
        self.file_label.config(text="Не обрано", fg="gray")

if __name__ == "__main__":
    root = Tk()
    app = GameTheoryApp(root)
    root.mainloop()
