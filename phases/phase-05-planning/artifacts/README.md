# Материалы Фазы 5 — календарно-ресурсное планирование

**Статус публикации:** все запланированные файлы загружены в GitHub; проверено 12.11.2026. Отчёты и изображения совпадают с итоговым комплектом по SHA.

## Отчёты и визуализация

| Файл | Назначение |
|---|---|
| [phase5-report.docx](phase5-report.docx) | Полный отчёт Word |
| [phase5-report.pdf](phase5-report.pdf) | PDF-версия отчёта (8 страниц) |
| [phase5-calculations.xlsx](phase5-calculations.xlsx) | Excel: WBS, график, 612 эвристик, этапы, итоги |
| [gantt.png](gantt.png) | Диаграмма Ганта проектных работ |

## Исходные данные и проверяемые результаты

| Файл | Назначение |
|---|---|
| [project_wbs.csv](project_wbs.csv) | Реестр 22 работ, ресурсы, длительности, предшественники |
| [resources.json](resources.json) | Сценарный штат: BAQA ×1, BE ×2, FE ×1 |
| [phase5_scheduler.py](phase5_scheduler.py) | RCPSP/SSGS, CPM, 12 заданных правил + 600 случайных |
| [best_schedule.csv](best_schedule.csv) | Лучший найденный календарно-ресурсный график 22 работ |
| [stage_milestones.csv](stage_milestones.csv) | Сроки восьми этапов |
| [heuristics_summary.csv](heuristics_summary.csv) | Сравнение 12 систематических правил и лучшего случайного |
| [heuristic_comparison.csv](heuristic_comparison.csv) | Полная таблица 612 вариантов |
| [schedule_results.json](schedule_results.json) | Контрольная сводка (193 рабочих дня) |

**Запуск:** установить `numpy` (`python -m pip install numpy`), затем выполнить `python phase5_scheduler.py` в каталоге, где находятся `project_wbs.csv` и `resources.json`. Программа заново создаст `heuristic_comparison.csv`, `best_schedule.csv`, `stage_milestones.csv` и `schedule_results.json`.

**Независимая проверка:** 22 работы и 612 вариантов присутствуют; все FS-зависимости соблюдены, дневная загрузка не превышает BAQA=1, BE=2, FE=1; лучший срок **193 рабочих дня**, **38,6 пятидневной недели**. Этот срок — *лучший найденный из проверенных вариантов*, а не доказанный глобальный минимум.

**Важное условие:** плановые длительности, состав специализаций и дата старта — учебная сценарная модель, согласованная командой со слов её представителя, но не фактически выполненный проект. [GitHub Issues #34–45](https://github.com/Vlad-gw/project-management/issues) закрыты как Completed после сообщения о согласовании команды 12.11.2026.

[Полный отчёт Фазы 5](../README.md).


**Подтверждение готовности:** [Согласование команды 12.11.2026](../../../docs/phase-04-05-team-approval-2026-11-12.md). Преподавательская приёмка Фаз 4–5 не заявляется.
