"""Учебная целочисленная модель распределения задач Фазы 3 (SciPy HiGHS).

ВАЖНО: оценки часов и предпочтений пока предварительные и должны быть
подтверждены всеми 4 участниками. После правок запустите скрипт повторно.

Установка: pip install scipy numpy
Запуск: python phase2_solver.py
"""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

MEMBERS = ['Владислав', 'Виталий', 'Елена', 'Антон']
CAPACITY = [40, 36, 32, 40]  # максимум человеко-часов для Фазы 3
TASKS = [('T01', 'Границы продукта, роли и акторы', 6, [4, 2, 2, 4]), ('T02', 'Каталог Use Cases и их классификация', 8, [5, 2, 3, 4]), ('T03', 'Основные, альтернативные и негативные сценарии', 18, [5, 2, 4, 3]), ('T04', 'UAW, UUCW и разбор транзакций UCP', 8, [2, 4, 5, 3]), ('T05', 'Технические и средовые поправки UCP', 10, [2, 3, 5, 3]), ('T06', 'Модель данных и карта COSMIC E/X/R/W', 20, [2, 5, 3, 1]), ('T07', 'Перепроверка COSMIC и устранение дублей', 12, [2, 5, 4, 3]), ('T08', 'Получение четырёх экспертных оценок UC', 8, [3, 3, 4, 5]), ('T09', 'Согласование, агрегация экспертных часов', 10, [3, 3, 4, 5]), ('T10', 'Сравнение методов, команда и сроки', 12, [5, 2, 4, 4]), ('T11', 'Подготовка отчёта Фазы 3', 14, [5, 2, 2, 3]), ('T12', 'Контроль качества и согласование итогов', 12, [3, 3, 4, 5])]

# x[i,j] = 1, если задача i закреплена за участником j.
# max Σ preference[i,j]*x[i,j]. scipy.milp минимизирует, поэтому c=-preference.
N = len(TASKS)
M = len(MEMBERS)
preferences = np.array([t[3] for t in TASKS], dtype=float)
hours = np.array([t[2] for t in TASKS], dtype=float)
constraints = []
lower, upper = [], []

# Каждая задача назначается ровно одному основному исполнителю.
for i in range(N):
    row = np.zeros(N*M)
    row[i*M:(i+1)*M] = 1
    constraints.append(row)
    lower.append(1)
    upper.append(1)

# Лимит трудоёмкости участника.
for j in range(M):
    row = np.zeros(N*M)
    row[j::M] = hours
    constraints.append(row)
    lower.append(0)
    upper.append(CAPACITY[j])

# Содержательное участие: каждому достаётся хотя бы 2 задачи.
for j in range(M):
    row = np.zeros(N*M)
    row[j::M] = 1
    constraints.append(row)
    lower.append(2)
    upper.append(N)

result = milp(
    c=-preferences.flatten(),
    integrality=np.ones(N*M, dtype=int),
    bounds=Bounds(np.zeros(N*M), np.ones(N*M)),
    constraints=LinearConstraint(np.array(constraints), lower, upper),
    options={"time_limit":30, "mip_rel_gap":1e-5},
)
if not result.success:
    raise RuntimeError("Оптимум не найден: " + str(result.message))
X = np.rint(result.x).astype(int).reshape(N, M)
print("\nОПТИМАЛЬНОЕ РАСПРЕДЕЛЕНИЕ")
print("-"*75)
for i, (code, name, effort, pref) in enumerate(TASKS):
    j = int(np.argmax(X[i]))
    print(f"{code} | {MEMBERS[j]:10s} | {effort:>4} ч | {pref[j]} баллов | {name}")
print("-"*75)
for j, name in enumerate(MEMBERS):
    used = float(sum(TASKS[i][2] * X[i,j] for i in range(N)))
    count = int(X[:,j].sum())
    print(f"{name:10s}: {used:.0f} / {CAPACITY[j]} ч, {count} задач")
assert np.all(X.sum(axis=1)==1)
assert all(np.dot(X[:,j],hours)<=CAPACITY[j] for j in range(M))
assert np.all(X.sum(axis=0)>=2)
print("Суммарная предпочтительность:", int(np.sum(preferences*X)))
print("Суммарные трудозатраты:", int(sum(hours)), "чел.-ч")
print("Условия проверены. Все оценки должны быть согласованы командой до сдачи.")
