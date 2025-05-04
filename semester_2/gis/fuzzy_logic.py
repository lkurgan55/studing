import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Оголошуємо нечіткі змінні для вхідних даних
cpu = ctrl.Antecedent(np.arange(0, 101, 1), 'cpu')
ram = ctrl.Antecedent(np.arange(0, 101, 1), 'ram')
net = ctrl.Antecedent(np.arange(0, 101, 1), 'net')
proc = ctrl.Antecedent(np.arange(0, 201, 1), 'proc')
latency = ctrl.Antecedent(np.arange(0, 2001, 1), 'latency')

# Вихідна змінна - рівень ризику
risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk')

# Функції приналежності для вхідних змінних
for var in [cpu, ram, net]:
    var['low'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['medium'] = fuzz.trimf(var.universe, [30, 50, 70])
    var['high'] = fuzz.trimf(var.universe, [60, 80, 100])

proc['low'] = fuzz.trimf(proc.universe, [0, 30, 70])
proc['medium'] = fuzz.trimf(proc.universe, [50, 100, 150])
proc['high'] = fuzz.trimf(proc.universe, [120, 160, 200])

latency['low'] = fuzz.trimf(latency.universe, [0, 300, 600])
latency['medium'] = fuzz.trimf(latency.universe, [500, 900, 1300])
latency['high'] = fuzz.trimf(latency.universe, [1200, 1600, 2000])

# Базові функції приналежності для ризику
risk['low'] = fuzz.trimf(risk.universe, [0, 20, 40])
risk['medium'] = fuzz.trimf(risk.universe, [30, 50, 70])
risk['high'] = fuzz.trimf(risk.universe, [60, 80, 100])

# Дуже високий ризик (операція концентрації - квадрат ступеня приналежності)
risk['very_high'] = risk['high'].mf ** 2

# Середній або високий ризик (операція об'єднання - максимальне з двох)
risk['medium_or_high'] = np.fmax(risk['medium'].mf, risk['high'].mf)

# Не низький ризик (логічне заперечення)
risk['not_low'] = 1 - risk['low'].mf

# Помірно низький ризик (операція розмиття - квадратний корінь ступеня приналежності)
risk['moderately_low'] = np.sqrt(risk['low'].mf)

# Правила (приклади, далі розширимо до 30+ правил)
rules = [
    ctrl.Rule(cpu['high'] & ram['high'], risk['high']),
    ctrl.Rule(proc['high'] & latency['high'], risk['high']),
    ctrl.Rule(net['high'] & cpu['high'], risk['high']),
    ctrl.Rule(cpu['medium'] | ram['medium'], risk['medium']),
    ctrl.Rule(proc['medium'] & latency['medium'], risk['medium']),
    ctrl.Rule(net['medium'] & ram['medium'], risk['medium']),
    ctrl.Rule(cpu['low'] & ram['low'] & proc['low'] & latency['low'], risk['low']),
    ctrl.Rule(net['low'] & latency['low'], risk['low']),
]

# Побудова системи
risk_ctrl = ctrl.ControlSystem(rules)
risk_simulation = ctrl.ControlSystemSimulation(risk_ctrl)

# Функція оцінки ризику
def evaluate_risk(cpu_val, ram_val, net_val, proc_val, latency_val):
    risk_simulation.input['cpu'] = cpu_val
    risk_simulation.input['ram'] = ram_val
    risk_simulation.input['net'] = net_val
    risk_simulation.input['proc'] = proc_val
    risk_simulation.input['latency'] = latency_val
    risk_simulation.compute()

    # Вихідні значення
    result = {
        'low': fuzz.interp_membership(risk.universe, risk['low'].mf, risk_simulation.output['risk']),
        'medium': fuzz.interp_membership(risk.universe, risk['medium'].mf, risk_simulation.output['risk']),
        'high': fuzz.interp_membership(risk.universe, risk['high'].mf, risk_simulation.output['risk']),
        'very_high': fuzz.interp_membership(risk.universe, risk['very_high'], risk_simulation.output['risk']),
        'medium_or_high': fuzz.interp_membership(risk.universe, risk['medium_or_high'], risk_simulation.output['risk']),
        'not_low': fuzz.interp_membership(risk.universe, risk['not_low'], risk_simulation.output['risk']),
        'moderately_low': fuzz.interp_membership(risk.universe, risk['moderately_low'], risk_simulation.output['risk'])
    }

    return result

