# expert_rules.py
from explanation import Explanation

def identify_virus_class(fuzzy_risk_levels, user_symptoms):
    explanation = Explanation()
    virus_classes = set()

    # Аналіз метрик
    if fuzzy_risk_levels['very_high'] > 0.7:
        explanation.add_step("Метрики вказують на дуже високий ризик.")
        virus_classes.update(['Ransomware', 'Trojan', 'Spyware'])
    elif fuzzy_risk_levels['medium_or_high'] > 0.5:
        explanation.add_step("Метрики вказують на середній або високий ризик.")
        virus_classes.update(['Trojan', 'Adware', 'Spyware'])

    # Аналіз симптомів
    symptom_mapping = {
        "Комп'ютер працює повільно": ['Spyware', 'Trojan'],
        "Програма не запускається": ['Trojan', 'Віруси'],
        "Відкриваються підозрілі вікна": ['Adware'],
        "Запуск невстановлених програм": ['Trojan'],
        "Браузер перенаправляє на невідомі сайти": ['Adware', 'Spyware'],
        "Файли зникають": ['Віруси', 'Ransomware'],
        "Файли заблоковані": ['Ransomware']
    }

    for symptom in user_symptoms:
        if symptom in symptom_mapping:
            matched_classes = symptom_mapping[symptom]
            explanation.add_step(f"Симптом '{symptom}' відповідає класам: {', '.join(matched_classes)}.")
            virus_classes.update(matched_classes)

    # Вибір фінального класу
    if 'Ransomware' in virus_classes:
        final_class = 'Ransomware'
    elif 'Trojan' in virus_classes:
        final_class = 'Trojan'
    elif 'Spyware' in virus_classes:
        final_class = 'Spyware'
    elif 'Adware' in virus_classes:
        final_class = 'Adware'
    elif 'Віруси' in virus_classes:
        final_class = 'Віруси'
    else:
        final_class = 'Шкідливе ПЗ (загальний клас)'

    return {
        'virus_class': final_class,
        'explanation': explanation.generate_explanation(final_class)
    }
