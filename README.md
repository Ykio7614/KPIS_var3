# ИПУР Desktop

Кроссплатформенное настольное приложение для расчёта интегрального показателя обоснованности управленческого решения (ИПУР) в подразделениях ИБ. Проект реализован строго по MVC: модели данных отделены от GUI, контроллер содержит только координацию и валидацию, а формулы вынесены в отдельный пакет `app/domain/formulas`.

Стек:
- Python 3.10+
- Tkinter для desktop GUI
- Matplotlib для трёх обязательных графиков
- PyInstaller для автономной упаковки под Windows/Linux/macOS

## Структура проекта

```text
lab1/
├── app/
│   ├── app.py                         # Точка сборки зависимостей и запуск приложения
│   ├── controllers/
│   │   ├── main_controller.py         # Связывает View и Model, обрабатывает события и импорт/экспорт
│   │   └── validation.py              # Валидация полей и сборка доменных объектов из формы/файлов
│   ├── domain/
│   │   └── formulas/
│   │       └── ipur.py                # Формула ИПУР и текстовая интерпретация результата
│   ├── models/
│   │   └── entities.py                # AppState, IndicatorInput, WeightSet, результаты, сценарии, периоды
│   ├── repositories/
│   │   ├── base.py                    # Абстракция репозитория
│   │   └── file_repository.py         # Реальное файловое хранилище JSON/CSV
│   ├── services/
│   │   ├── import_export_service.py   # Импорт/экспорт состояния приложения
│   │   └── report_service.py          # Экспорт печатных HTML- и PDF-отчётов
│   ├── utils/
│   │   └── constants.py               # Предустановки весов
│   └── views/
│       └── main_view.py               # GUI: форма, таблицы, кнопки, диалоги, графики
├── docs/
│   └── examples/
│       ├── sample_data.csv            # Пример CSV с текущим расчётом, периодами и сценариями
│       └── sample_data.json           # Пример JSON в полной структуре состояния
├── tests/
│   ├── test_import_export.py          # Проверки загрузки/сохранения JSON/CSV
│   └── test_ipur.py                   # Проверки формулы и сценариев I/II/III
├── main.py                            # Входная точка desktop-приложения
├── pyproject.toml                     # Метаданные и зависимости Python
└── README.md                          # Инструкция по запуску, сборке и форматам
```

## Формула и интерпретация

Реализован смысл ТЗ:

```text
I = aR * R + aS * S + aE * E
```

где:
- `R` — ретроспективные данные
- `S` — текущая статистическая информация
- `E` — экспертная оценка
- `aR + aS + aE = 1`

Интерпретация:
- `I >= 0.6` — высокий уровень защищённости
- `0.4 <= I < 0.6` — удовлетворительный уровень
- `I < 0.4` — повышенный риск

## Функции приложения

- Ввод `R`, `S`, `E` и весов `aR`, `aS`, `aE` вручную.
- Три предустановки весов:
  - стандартный: `0.3 / 0.5 / 0.2`
  - консервативный: `0.5 / 0.3 / 0.2`
  - оперативный: `0.2 / 0.6 / 0.2`
- Немедленный расчёт результата `I` с текстовой интерпретацией.
- Таблица текущих входных данных.
- График 1: вклад `R`, `S`, `E` и итогового `I`.
- График 2: динамика `I` по периодам.
- График 3: сравнение 2–3 сценариев.
- Загрузка данных из `JSON` и `CSV`.
- Сохранение состояния в `JSON`, экспорт в `CSV`, экспорт отчёта в `HTML` и `PDF`.
- Простые русские сообщения об ошибках.

## UX и валидация

- Все значения `R`, `S`, `E`, `aR`, `aS`, `aE` проверяются на диапазон `[0, 1]`.
- Для ручного ввода весов выбрана **явная ошибка**, а не автонормализация. Причина: веса отражают смысловую приоритизацию источников данных, и скрытое изменение коэффициентов системой могло бы исказить решение ЛПР. Приложение показывает понятную ошибку, если сумма весов не равна `1`.

## Формат JSON

`JSON` хранит полное состояние приложения: текущий расчёт, периоды и сценарии.

Пример: [docs/examples/sample_data.json](/Users/andrej/Documents/Учеба/kpis/lab1/docs/examples/sample_data.json)

Ключи:
- `current_input`
- `current_result`
- `periods[]`
- `scenarios[]`

## Формат CSV

`CSV` содержит плоские строки с типом записи:

```text
type,name,R,S,E,aR,aS,aE,I,interpretation
current,Текущий расчёт,0.7,0.733,0.35,0.3,0.4,0.3,0.608,...
period,2026-03,0.7,0.733,0.35,0.3,0.4,0.3,0.608,...
scenario,Сценарий I,0.7,0.733,0.35,0.3,0.4,0.3,0.608,...
```

Пример: [docs/examples/sample_data.csv](/Users/andrej/Documents/Учеба/kpis/lab1/docs/examples/sample_data.csv)

## Запуск в dev-режиме

1. Создать виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Установить зависимости:

```bash
python -m pip install --upgrade pip
python -m pip install .
```

3. Запустить приложение:

```bash
python main.py
```

Примечание для Linux/Astra Linux: для dev-режима нужен Tk runtime. Обычно это пакет `python3-tk` или эквивалент дистрибутива.

## Сборка и пакетирование

Установить инструмент упаковки:

```bash
python -m pip install pyinstaller
```

### Windows

```powershell
py -3 -m pip install .
py -3 -m pip install pyinstaller
py -3 -m PyInstaller --noconfirm --clean --windowed --name IPUR --collect-data matplotlib main.py
Compress-Archive -Path dist\IPUR\* -DestinationPath dist\IPUR-windows.zip
```

Результат: каталог `dist\IPUR\` и архив `dist\IPUR-windows.zip`.

### Linux / Astra Linux

```bash
python3 -m pip install .
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name IPUR --collect-data matplotlib main.py
tar -C dist -czf dist/ipur-linux.tar.gz IPUR
```

Результат: каталог `dist/IPUR/` и архив `dist/ipur-linux.tar.gz`.

### macOS

```bash
python3 -m pip install .
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --clean --windowed --name IPUR --collect-data matplotlib main.py
ditto -c -k --sequesterRsrc --keepParent dist/IPUR.app dist/IPUR-macos.zip
```

Результат: приложение `dist/IPUR.app` и архив `dist/IPUR-macos.zip`.

Важно: сборку нужно выполнять на целевой ОС. PyInstaller не делает кросс-компиляцию между Windows/Linux/macOS.

## Демонстрация расчётов по ТЗ

Сценарий I:
- `R = 0.7`, `aR = 0.3`
- `S = 0.733`, `aS = 0.4`
- `E = 0.35`, `aE = 0.3`
- `I = 0.3*0.7 + 0.4*0.733 + 0.3*0.35 = 0.608`
- интерпретация: высокий уровень защищённости

Сценарий II:
- `R = 0.8`, `aR = 0.2`
- `S = 0.0`, `aS = 0.6`
- `E = 0.4`, `aE = 0.2`
- `I = 0.2*0.8 + 0.6*0.0 + 0.2*0.4 = 0.240`
- интерпретация: повышенный риск

Сценарий III:
- `R = 0.3`, `aR = 0.4`
- `S = 0.5`, `aS = 0.3`
- `E = 0.8`, `aE = 0.3`
- `I = 0.4*0.3 + 0.3*0.5 + 0.3*0.8 = 0.510`
- интерпретация: удовлетворительный уровень

## Проверка

Быстрые тесты:

```bash
python -m pytest
```

Если `pytest` не установлен:

```bash
python -m unittest discover -s tests
```
