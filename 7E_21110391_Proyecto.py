import json
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog  # Importamos simpledialog correctamente

# Archivos para guardar las bases de datos
QUESTIONS_FILE = "questions_db.json"
SOLUTIONS_FILE = "solutions_db.json"

# Cargar o inicializar las bases de datos
def load_database(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_database(file_path, database):
    with open(file_path, "w") as file:
        json.dump(database, file, indent=4)

# Motor de inferencia (Forward Chaining)
def infer_solution(answers, solutions):
    for solution in solutions:
        if all(answers.get(factor["factor"], False) == factor["expected"] for factor in solution["rules"]):
            return solution["description"]
    return "No se pudo determinar una solución con las respuestas proporcionadas."

# Interfaz gráfica
class ExpertSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Experto - Diagnóstico de Computadoras")
        self.questions_db = load_database(QUESTIONS_FILE)
        self.solutions_db = load_database(SOLUTIONS_FILE)
        self.answers = {}

        # Crear interfaz
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20)

        self.title_label = tk.Label(self.main_frame, text="Diagnóstico de Computadoras", font=("Arial", 16))
        self.title_label.pack()

        self.start_button = tk.Button(self.main_frame, text="Iniciar Diagnóstico", command=self.start_diagnosis)
        self.start_button.pack(pady=10)

        self.manage_button = tk.Button(self.main_frame, text="Administrar Base de Datos", command=self.manage_database)
        self.manage_button.pack(pady=10)

    # Iniciar diagnóstico
    def start_diagnosis(self):
        self.answers = {}
        for question in self.questions_db:
            answer = messagebox.askyesno("Pregunta", question["text"])
            self.answers[question["factor"]] = answer

        solution = infer_solution(self.answers, self.solutions_db)
        messagebox.showinfo("Resultado", solution)

    # Administrar la base de datos
    def manage_database(self):
        self.manage_window = tk.Toplevel(self.root)
        self.manage_window.title("Administrar Base de Datos")

        self.add_question_button = tk.Button(self.manage_window, text="Agregar Pregunta", command=self.add_question)
        self.add_question_button.pack(pady=5)

        self.add_solution_button = tk.Button(self.manage_window, text="Agregar Solución", command=self.add_solution)
        self.add_solution_button.pack(pady=5)

        self.edit_questions_button = tk.Button(self.manage_window, text="Editar Preguntas", command=lambda: self.edit_database("questions"))
        self.edit_questions_button.pack(pady=5)

        self.edit_solutions_button = tk.Button(self.manage_window, text="Editar Soluciones", command=lambda: self.edit_database("solutions"))
        self.edit_solutions_button.pack(pady=5)

    # Agregar pregunta
    def add_question(self):
        question_text = simpledialog.askstring("Nueva Pregunta", "Ingresa el texto de la pregunta (Sí/No):")
        if question_text:
            factor = simpledialog.askstring("Factor", "Ingresa el factor asociado a esta pregunta:")
            if factor:
                self.questions_db.append({"text": question_text, "factor": factor})
                save_database(QUESTIONS_FILE, self.questions_db)
                messagebox.showinfo("Éxito", "Pregunta agregada correctamente.")

    # Agregar solución
    def add_solution(self):
        description = simpledialog.askstring("Nueva Solución", "Describe la solución:")
        if description:
            rules = []
            while True:
                factor = self.select_factor_with_combobox()
                if not factor:
                    break
                expected = messagebox.askyesno("Respuesta esperada", f"¿La respuesta esperada para {factor} es 'Sí'?")
                rules.append({"factor": factor, "expected": expected})

            self.solutions_db.append({"description": description, "rules": rules})
            save_database(SOLUTIONS_FILE, self.solutions_db)
            messagebox.showinfo("Éxito", "Solución agregada correctamente.")

    # Seleccionar factor con Combobox
    def select_factor_with_combobox(self):
        if not self.questions_db:
            messagebox.showwarning("Error", "No hay factores disponibles. Agrega preguntas primero.")
            return None

        select_window = tk.Toplevel(self.root)
        select_window.title("Seleccionar Factor")

        tk.Label(select_window, text="Selecciona un factor:").pack(pady=5)
        factor_var = tk.StringVar()

        factors = [question["factor"] for question in self.questions_db]
        combobox = ttk.Combobox(select_window, textvariable=factor_var, values=factors, state="readonly")
        combobox.pack(pady=5)
        combobox.current(0)

        def confirm_selection():
            selected = combobox.get()
            select_window.destroy()
            self.selected_factor = selected

        self.selected_factor = None
        tk.Button(select_window, text="Aceptar", command=confirm_selection).pack(pady=5)
        select_window.wait_window()

        return self.selected_factor

    # Editar o eliminar entradas de la base de datos
    def edit_database(self, db_type):
        db = self.questions_db if db_type == "questions" else self.solutions_db
        file_path = QUESTIONS_FILE if db_type == "questions" else SOLUTIONS_FILE
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar {'Preguntas' if db_type == 'questions' else 'Soluciones'}")

        for i, entry in enumerate(db):
            frame = tk.Frame(edit_window)
            frame.pack(pady=5, padx=10, fill="x")

            label_text = entry["text"] if db_type == "questions" else entry["description"]
            entry_label = tk.Label(frame, text=f"{i + 1}. {label_text}")
            entry_label.pack(side="left")

            delete_button = tk.Button(frame, text="Eliminar", command=lambda idx=i: self.delete_entry(db, idx, file_path, edit_window))
            delete_button.pack(side="right")

            if db_type == "questions":
                edit_button = tk.Button(frame, text="Editar", command=lambda idx=i: self.edit_question(idx, edit_window))
                edit_button.pack(side="right")
            else:
                edit_button = tk.Button(frame, text="Editar", command=lambda idx=i: self.edit_solution(idx, edit_window))
                edit_button.pack(side="right")

    # Eliminar una entrada
    def delete_entry(self, db, idx, file_path, window):
        del db[idx]
        save_database(file_path, db)
        messagebox.showinfo("Éxito", "Entrada eliminada correctamente.")
        window.destroy()
        self.edit_database("questions" if file_path == QUESTIONS_FILE else "solutions")

        # Editar una pregunta
    def edit_question(self, idx, window):
        question_text = simpledialog.askstring("Editar Pregunta", "Ingresa el nuevo texto de la pregunta:", initialvalue=self.questions_db[idx]["text"])
        if question_text:
            factor = simpledialog.askstring("Editar Factor", "Ingresa el nuevo factor asociado:", initialvalue=self.questions_db[idx]["factor"])
            if factor:
                self.questions_db[idx] = {"text": question_text, "factor": factor}
                save_database(QUESTIONS_FILE, self.questions_db)
                messagebox.showinfo("Éxito", "Pregunta editada correctamente.")
                window.destroy()
                self.edit_database("questions")

    #Editar Solución
    def edit_solution(self, idx, window):
        solution = self.solutions_db[idx]
        description = simpledialog.askstring("Editar Solución", "Describe la solución:", initialvalue=solution["description"])
        if description:
            rules = []
            for rule in solution["rules"]:
                factor = rule["factor"]
                expected = messagebox.askyesno("Editar Regla", f"¿La respuesta esperada para {factor} sigue siendo 'Sí'?")
                rules.append({"factor": factor, "expected": expected})
            self.solutions_db[idx] = {"description": description, "rules": rules}
            save_database(SOLUTIONS_FILE, self.solutions_db)
            messagebox.showinfo("Éxito", "Solución editada correctamente.")
            window.destroy()
            self.edit_database("solutions")

# Correr la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpertSystemApp(root)
    root.mainloop()
