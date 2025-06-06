class Explanation:
    def __init__(self):
        self.steps = []  # список кроків, які виконалися для прийняття рішення

    def add_step(self, step_description):
        # Додаємо опис кожного кроку
        print(step_description)
        self.steps.append(step_description)

    def generate_explanation(self, final_class):
        # Формуємо фінальне пояснення
        explanation_text = f"Експертна система визначила клас загрози як: {final_class}\n\n"
        explanation_text += "Пояснення висновку:\n"

        for i, step in enumerate(self.steps, 1):
            explanation_text += f"{i}. {step}\n"

        return explanation_text
