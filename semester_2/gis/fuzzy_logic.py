import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Оголошуємо нечіткі змінні для вхідних даних
cpu = ctrl.Antecedent(np.arange(0, 101, 1), 'cpu')
ram = ctrl.Antecedent(np.arange(0, 101, 1), 'ram')
net = ctrl.Antecedent(np.arange(0, 101, 1), 'net')
proc = ctrl.Antecedent(np.arange(0, 501, 1), 'proc')
latency = ctrl.Antecedent(np.arange(0, 2001, 1), 'latency')

# Вихідна змінна - рівень ризику
risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk')

# Функції приналежності для вхідних змінних
for var in [cpu, ram, net]:
    var['low'] = fuzz.trimf(var.universe, [0, 20, 40]) # 0-20 - low->1, 20-40 - low -> 0
    var['medium'] = fuzz.trimf(var.universe, [30, 50, 70])
    var['high'] = fuzz.trimf(var.universe, [60, 80, 100])

proc['low'] = fuzz.trimf(proc.universe, [0, 100, 200])
proc['medium'] = fuzz.trimf(proc.universe, [200, 300, 450])
proc['high'] = fuzz.trimf(proc.universe, [400, 450, 500])

latency['low'] = fuzz.trimf(latency.universe, [0, 300, 600])
latency['medium'] = fuzz.trimf(latency.universe, [500, 900, 1300])
latency['high'] = fuzz.trimf(latency.universe, [1200, 1600, 2000])

# Базові функції приналежності для ризику
risk['low'] = fuzz.trimf(risk.universe, [0, 20, 40])
risk['medium'] = fuzz.trimf(risk.universe, [30, 50, 70])
risk['high'] = fuzz.trimf(risk.universe, [60, 80, 100])

# Правила
rules = [
    ctrl.Rule(cpu['high'] & ram['high'], risk['high']),
    ctrl.Rule(proc['high'] & latency['high'], risk['high']),
    ctrl.Rule(net['high'] & cpu['high'], risk['high']),
    ctrl.Rule(cpu['high'] & proc['medium'], risk['high']),
    ctrl.Rule(net['high'] & ram['medium'], risk['high']),
    ctrl.Rule(net['medium'] & proc['high'], risk['high']),
    ctrl.Rule(cpu['medium'] & net['high'], risk['high']),
    ctrl.Rule(cpu['medium'] & ram['medium'] & latency['medium'], risk['medium']),
    ctrl.Rule(cpu['medium'] | ram['medium'], risk['medium']),
    ctrl.Rule(proc['medium'] & latency['medium'], risk['medium']),
    ctrl.Rule(net['medium'] & ram['medium'], risk['medium']),
    ctrl.Rule(cpu['low'] & ram['low'] & proc['low'] & latency['low'], risk['low']),
    ctrl.Rule(net['low'] & latency['low'], risk['low']),
    ctrl.Rule(proc['low'] & latency['low'] & cpu['low'], risk['low']),
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

    base_low = fuzz.interp_membership(risk.universe, risk['low'].mf, risk_simulation.output['risk'])
    base_med = fuzz.interp_membership(risk.universe, risk['medium'].mf, risk_simulation.output['risk'])
    base_high = fuzz.interp_membership(risk.universe, risk['high'].mf, risk_simulation.output['risk'])

    # Побудова додаткових логічних рівнів
    result = {
        'low': base_low,
        'medium': base_med,
        'high': base_high,
        'very_high': base_high ** 2,
        'medium_or_high': np.fmax(base_med, base_high),
        'not_low': 1 - base_low,
        'moderately_low': np.sqrt(base_low)
    }

    return result