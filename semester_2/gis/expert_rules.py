from explanation import Explanation

def ask_user(symptom_text):
    response = input(f"{symptom_text}? (так/ні): ").strip().lower()
    return response in ['так', 'yes', 'y']

def identify_virus_class(fuzzy_risk_levels):
    explanation = Explanation()
    class_scores = {}
    user_symptoms = []

    # Етап 1: Аналіз метрик і рівня ризику
    if fuzzy_risk_levels['low'] > 0.7:
        explanation.add_step("Метрики вказують на низьке навантаження. Немає загрози.")
        return {
            'virus_class': 'Немає загроз',
            'explanation': explanation.generate_explanation('Немає загроз')
        }
    elif fuzzy_risk_levels['very_high'] > 0.8:
        explanation.add_step("Виявлено критичний рівень ризику. Пропускаємо загальні питання і переходимо до класифікації ШПЗ.")
    elif fuzzy_risk_levels['medium_or_high'] > 0.5:
        explanation.add_step("Метрики вказують на середнє або високе навантаження. Починаємо перевірку на зараження.")

        # Етап 2: Загальні питання
        general_symptoms = [
            "Комп'ютер працює повільніше, ніж зазвичай",
            "Система довго запускається або вимикається",
            "Періодично з’являються помилки або збої без причин",
            "Несподіване підвищення використання ЦП або ОЗУ",
            "Час відгуку на відкриття вікон/файлів сильно зріс",
            "Поява нових процесів у диспетчері задач, які не зрозумілі",
            "Виникають проблеми з підключенням до Інтернету",
            "Виникають проблеми з доступом до файлів або папок",
            "Виникнення «зависань» або «мертвих зон» у системі",
            "Періодичне автоматичне перезавантаження системи"
        ]
        has_yes = 0
        for s in general_symptoms:
            if has_yes >= 3: # якщо 3 сиптомів то ймовірне зараження і переходимо до наступного етапу
                break
            if ask_user(s):
                has_yes += 1

        if not has_yes:
            explanation.add_step("Загальні симптоми зараження не виявлено. Система, ймовірно, не інфікована.")
            return {
                'virus_class': 'Немає загроз',
                'explanation': explanation.generate_explanation('Немає загроз')
            }

        explanation.add_step("Виявлено загальні симптоми. Переходимо до класифікації ШПЗ.")
    else:
        explanation.add_step("Рівень ризику не є достатньо високим для подальшого аналізу.")
        return {
            'virus_class': 'Немає загроз',
            'explanation': explanation.generate_explanation('Немає загроз')
        }

    # Етап 3: Спільні симптоми
    shared_symptoms_map = {
        "Браузер перенаправляє на невідомі сайти": ['Adware', 'Spyware'],
        "Підозріла передача даних": ['Spyware', 'Ransomware'],
        "Запуск невстановлених програм": ['Trojan', 'Spyware'],
        "Файли зникають": ['Ransomware', 'Trojan'],
        "Програма не запускається": ['Trojan', 'Ransomware'],
        "Зміна домашньої сторінки у браузері": ['Adware', 'Spyware'],
        "Не вдається оновити антивірус": ['Trojan', 'Ransomware'],
        "Постійно з'являються нові ярлики на робочому столі": ['Adware', 'Trojan'],
        "Підозрілі процеси активно використовують мережу": ['Spyware', 'Ransomware'],
        "В системі з’явились незрозумілі нові користувачі": ['Trojan', 'Spyware'],
        "Деякі налаштування системи стали недоступні": ['Trojan', 'Ransomware'],
        "Браузер сам відкриває вкладки з рекламою": ['Adware', 'Spyware']
    }

    for symptom, classes in shared_symptoms_map.items():
        if ask_user(symptom):
            user_symptoms.append(symptom)
            for cls in classes:
                class_scores[cls] = class_scores.get(cls, 0) + 1
            explanation.add_step(f"Симптом '{symptom}' збільшує ймовірність: {', '.join(classes)}")

    if not class_scores:
        explanation.add_step("Жоден із симптомів не вказує на ймовірний клас. Переходимо до точного визначення.")
    else:
        explanation.add_step(f"Визначено попередній набір ймовірних класів загроз: {set(class_scores.keys())}.")

    # Етап 4: Унікальні симптоми лише для ймовірних класів
    unique_symptoms_map = {
        "Файли заблоковані або зашифровані": 'Ransomware',
        "Відображається повідомлення з вимогою викупу": 'Ransomware',
        "З'явилися нові незрозумілі адміністраторські облікові записи": 'Trojan',
        "Змінено системні політики без вашого втручання": 'Trojan',
        "Підозра на витік паролів або конфіденційних даних": 'Spyware',
        "На сайтах вводяться дані самостійно": 'Spyware',
        "На екрані з'являються банери або спливаючі рекламні вікна": 'Adware',
        "Реклама з'являється навіть у програмах без інтернету": 'Adware'
    }

    probable_classes = set(class_scores.keys())
    for symptom, virus in unique_symptoms_map.items():
        if virus in probable_classes:
            if ask_user(symptom):
                explanation.add_step(f"Унікальний симптом '{symptom}' однозначно вказує на '{virus}'.")
                return {
                    'virus_class': virus,
                    'explanation': explanation.generate_explanation(virus)
                }

    # Етап 5: Вибір найбільш ймовірного класу
    if class_scores:
        best_match = max(class_scores, key=class_scores.get)
        explanation.add_step(f"Клас з найбільшою кількістю збігів: {best_match}.")
        return {
            'virus_class': best_match,
            'explanation': explanation.generate_explanation(best_match)
        }

    return {
        'virus_class': 'Шкідливе ПЗ',
        'explanation': explanation.generate_explanation('Шкідливе ПЗ')
    }