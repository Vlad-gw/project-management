# Артефакты Фазы 5 — Календарно-ресурсный график

**Опубликованы в ветке main:** WBS, модель ресурсов, код планировщика, лучшее расписание, этапы, сравнение правил и JSON. Подробная методика — [README Фазы 5](../README.md).

| Файл | Назначение |
|---|---|
| [project_wbs.csv](project_wbs.csv) | 22 задачи разработки, длительности, предшественники и потребности |
| [resources.json](resources.json) | Команда BAQA ×1, BE ×2, FE ×1, календарь 8/40 |
| [phase5_scheduler.py](phase5_scheduler.py) | RCPSP/SSGS, CPM, 12 заданных правил и 600 случайных приоритетов |
| [best_schedule.csv](best_schedule.csv) | Лучший график 22 работ с ES/EF/LS/LF |
| [stage_milestones.csv](stage_milestones.csv) | Сроки этапов, перекрытия этапов |
| [heuristics_summary.csv](heuristics_summary.csv) | 12 заданных правил и лучший случайный вариант |
| [schedule_results.json](schedule_results.json) | Итог: 193 рабочих дня, 38,6 недели |

**Запуск:** `python -m pip install numpy`, затем `python phase5_scheduler.py`. Скрипт повторно формирует `best_schedule.csv`, `stage_milestones.csv`, `schedule_results.json` и полный `heuristic_comparison.csv` на все 612 испытаний (12 систематических + 600 случайных).

**Статус:** это проверенный сценарный ресурсный график, **не утверждённые командой длительности или штат**. Отчёт Word/PDF и расчётная книга Excel подготовлены отдельным скачиваемым комплектом, но **бинарные файлы здесь пока не опубликованы**. Вся вычислительная база и самодостаточное описание доступны непосредственно в GitHub.
