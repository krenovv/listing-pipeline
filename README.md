# Listing Pipeline

Automation toolkit for marketplace workflows, including listing creation, payment processing, and content preparation.

> Built to automate a real workflow with 500–800 listings per week on the Meshok marketplace.

---

## Overview

Listing Pipeline is a modular system designed to automate repetitive operations in marketplace workflows.

It was developed for a real-world process on the Meshok platform and covers not only listing creation, but also related tasks such as payment tracking, data processing, and content preparation.

The system focuses on speed, consistency, and reducing manual work.

---

## Features

### Listing Automation
- Title formatting from inconsistent raw input  
- Tag generation (SEO-oriented)  
- Sequential listing time scheduling  
- Lot parsing from copied marketplace content  

### Financial Processing
- Parsing bank statements (PDF / text) from multiple banks  
- Unified transaction model  
- Search by amount  
- Filtering by date  
- Aggregation by account  

### Data Processing
- Parsing deal lists and aggregating sums by buyer  
- Clipboard-based workflow for fast operations  

### Content Preparation
- Certificate text generation for CorelDRAW  
- Bulk image workflow using browser automation (Tampermonkey)  

### Integration
- Airtable synchronization (automatic title + image extraction from Meshok links)  

### Workflow
- Interactive console interface  
- Clipboard-driven operations (minimal manual input)  

---

## Architecture

The project follows a modular structure:

- **core/** — business logic (formatting, parsing, tags, certificates)  
- **services/** — data processing (bank operations, deal aggregation)  
- **integrations/** — external services (Airtable)  
- **utils/** — shared utilities  
- **interfaces/** — CLI and interactive workflow  
- **tools/** — auxiliary tools (e.g. browser automation scripts)  

---

## Workflow

Optimized for fast repetitive operations:

1. Copy raw data (title, deals, bank data, etc.)  
2. Run the corresponding module  
3. Result is automatically copied to clipboard  
4. Paste into target system  

---

## Why this project

The project was created to solve real operational problems:

- Inconsistent raw data required manual cleanup  
- Managing hundreds of listings per week was time-consuming  
- Payment verification required manual search across multiple banks  
- Image uploads and content preparation were slow  

Listing Pipeline automates these processes and makes the workflow faster, more consistent, and easier to manage.

---

# Listing Pipeline (RU)

Система автоматизации процессов работы с маркетплейсами: создание лотов, обработка платежей и подготовка контента.

> Создано для реального сценария с 500–800 лотами в неделю на площадке Мешок.

---

## Описание

Listing Pipeline — это модульная система для автоматизации рутинных операций при работе с маркетплейсами.

Проект разработан на основе реального процесса и охватывает:
- создание лотов  
- обработку платежей  
- подготовку контента  
- работу с данными  

Основная цель — ускорение работы, снижение количества ручных операций и повышение стабильности процесса.

---

## Возможности

### Работа с лотами
- Форматирование названий  
- Генерация тегов  
- Планирование времени публикации  
- Парсинг списка лотов  

### Финансы
- Парсинг банковских выписок (PDF / TXT)  
- Поиск операций по сумме  
- Фильтрация по дате  
- Агрегация по аккаунтам  

### Обработка данных
- Парсинг сделок и суммирование по покупателям  

### Подготовка контента
- Генерация текста для сертификатов  
- Массовая работа с изображениями (через Tampermonkey)  

### Интеграции
- Синхронизация с Airtable  

### Интерфейс
- Интерактивный консольный режим  
- Работа через буфер обмена  

---

## Архитектура

Проект разделён на модули:

- **core/** — бизнес-логика  
- **services/** — обработка данных  
- **integrations/** — внешние сервисы  
- **utils/** — вспомогательные функции  
- **interfaces/** — интерфейс  
- **tools/** — дополнительные инструменты  

---

## Workflow

Работа строится в быстром цикле:

1. Скопировать данные  
2. Запустить нужный модуль  
3. Получить результат (в буфере обмена)  
4. Вставить в нужную систему  

---

## Зачем этот проект

В исходном процессе:

- данные приходили в разном формате  
- требовалась ручная обработка  
- работа с платежами занимала много времени  
- загрузка изображений была неудобной  

Система автоматизирует эти задачи и делает процесс быстрее, понятнее и устойчивее.