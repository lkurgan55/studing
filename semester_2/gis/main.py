# main.py

from fuzzy_logic import evaluate_risk
from expert_rules import identify_virus_class
from symptom_analysis import get_user_symptoms
from recommendations import get_recommendations
import psutil
import time

# Функція для отримання поточних значень метрик
def get_current_metrics():
    cpu_val = psutil.cpu_percent(interval=1)
    ram_val = psutil.virtual_memory().percent
    net_val = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    net_val_mb = net_val / (1024 * 1024)  # Мегабайти за час моніторингу

    proc_val = len(psutil.pids())

    start_time = time.time()
    time.sleep(0.1)  # Штучна затримка для вимірювання часу відгуку
    latency_val = (time.time() - start_time) * 1000  # у мілісекундах

    # Нормалізація значень мережі до %
    net_val_normalized = min(net_val_mb / 10, 100)  # умовна нормалізація

    return cpu_val, ram_val, net_val_normalized, proc_val, latency_val

def main():
    choice = input("Оберіть спосіб отримання метрик:\n"
                   "[1] Ввести вручну\n"
                   "[2] Використати поточні значення системи\n"
                   "Ваш вибір (1/2): ").strip()

    if choice == '2':
        print("\nОтримуємо поточні значення системних параметрів...\n")
        cpu_val, ram_val, net_val, proc_val, latency_val = get_current_metrics()
        print(f"CPU: {cpu_val:.2f}%")
        print(f"RAM: {ram_val:.2f}%")
        print(f"Мережа: {net_val:.2f}%")
        print(f"Кількість процесів: {proc_val}")
        print(f"Час відгуку: {latency_val:.2f} мс\n")
    else:
        cpu_val = float(input("Введіть завантаження CPU (0-100%): "))
        ram_val = float(input("Введіть завантаження RAM (0-100%): "))
        net_val = float(input("Введіть завантаження мережі (0-100%): "))
        proc_val = int(input("Введіть кількість активних процесів: "))
        latency_val = float(input("Введіть час відгуку системи (в мс): "))

    # Аналіз метрик за допомогою нечіткої логіки
    fuzzy_result = evaluate_risk(cpu_val, ram_val, net_val, proc_val, latency_val)
    print("Аналіз метрик за допомогою нечіткої логіки завершено\n")

    # Якщо ризик хоча б середній, уточнюємо симптоми у користувача
    if fuzzy_result['medium_or_high'] > 0.5:
        user_symptoms = get_user_symptoms()
    else:
        user_symptoms = []
        print("Система визначила низький ризик, додаткові питання не потрібні.\n")

    # Виклик експертної системи
    result = identify_virus_class(fuzzy_result, user_symptoms)

    # Вивід фінального класу вірусу
    print("\nФінальний клас загрози:", result['virus_class'])

    # Вивід пояснення рішення
    print(result['explanation'])

    # Вивід рекомендацій
    recommendations = get_recommendations(result['virus_class'], fuzzy_result)
    print("\nРекомендації:")
    for recommendation in recommendations:
        print("-", recommendation)

if __name__ == "__main__":
    main()
