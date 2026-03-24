# Listing Pipeline

Automation toolkit for marketplace workflows, including listing creation, scheduling, and payment processing.

> Built to automate a real workflow with 500–800 listings per week on the Meshok marketplace.

---

## Overview

Listing Pipeline is a system designed to automate repetitive tasks in marketplace operations.

It was developed for a real-world workflow on the Meshok platform, covering not only listing creation, but also related operational tasks such as payment tracking and content handling.

The system focuses on speed, reducing manual work, and making the workflow predictable and consistent.

---

## Features

- Title formatting based on inconsistent raw input  
- Automatic tag generation (SEO-oriented)  
- Listing time scheduling for auction workflows  
- Lot parsing from copied marketplace content  
- Payment processing support (bank statement parsing)  
- Bulk image handling for listing creation  
- Interactive workflow mode (Enter-driven)  
- Clipboard integration for minimal manual input  

---

## Architecture

The project follows a modular structure:

- **core/** — business logic (formatting, parsing, tags, data processing)  
- **interfaces/** — CLI and interactive interface  
- **tools/**  — auxiliary user tools (e.g. AHK macros) for workflow acceleration
- **utils/** — reusable components (time generator, helpers)

---

## Workflow

The system is optimized for fast repetitive processing:

1. Copy raw title  
2. Press Enter > formatted title (copied to clipboard)  
3. Press Enter > next listing time  
4. Press Enter > generated tags  
5. Repeat for next item  

Additional modules support payment verification and content preparation.

---

## Why this project

The project was created to solve practical problems in a real workflow:

- Raw data (titles, descriptions) was inconsistent and required manual cleanup  
- Listing hundreds of items per week was time-consuming  
- Payment verification required manual search across multiple bank accounts  
- Uploading images was slow and repetitive  

Listing Pipeline automates these processes, reduces manual effort, and significantly speeds up daily operations.

---

# Listing Pipeline (RU)

Система автоматизации процессов работы с маркетплейсами: создание лотов, планирование, обработка платежей и подготовка контента.

> Создано для реального сценария с 500–800 лотами в неделю на площадке Мешок.

---

## Описание

Listing Pipeline — это инструмент для автоматизации рутинных операций в работе с маркетплейсами.

Он был разработан под реальный процесс на площадке Мешок и охватывает не только создание лотов, но и сопутствующие задачи: обработку платежей и работу с контентом.

Основная цель — ускорение работы, снижение ручного труда и повышение стабильности процесса.

---

## Возможности

- Форматирование названий из "сырого" ввода  
- Генерация тегов  
- Планирование времени публикации  
- Парсинг лотов из скопированного текста  
- Обработка банковских операций (по выпискам)  
- Массовая работа с изображениями

---

## Архитектура

Проект построен модульно:

- **core/** — бизнес-логика  
- **interfaces/** — интерфейсы взаимодействия
- **tools/** — вспомогательные инструменты  
- **utils/** — утилиты  


---

## Workflow

Оптимизирован под быстрый цикл работы:

1. Скопировать сырое название  
2. Enter > получить отформатированное название  
3. Enter > получить время публикации  
4. Enter > получить теги  
5. Повторить  

Дополнительные модули используются для проверки оплат и подготовки изображений.

---

## Зачем этот проект

В исходном процессе:

- названия приходили в разном формате  
- требовалась ручная правка  
- выставление сотен лотов занимало много времени  
- проверка оплат занимала много времени из-за нескольких банков  
- загрузка изображений была медленной и неудобной  

Система автоматизирует эти шаги и делает процесс быстрее, понятнее и устойчивее.