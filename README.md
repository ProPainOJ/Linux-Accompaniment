# <center>Linux-Accompaniment</center>
###### _Программа для вывода напоминаний, логирования времени работы и другого вспомогательного функционала работы в linux._
<hr>

# Оглавление :page_with_curl:

1. [Установка](#установка)
2. [Зависимости](#зависимости)
    - [Linux packages](#linux-packages)
    - [Docker](#docker)
    - [App](#app)
3. [Настройка приложения](#настройка-приложения)

<hr>

## Установка

Перейти в директорию для установки.

```bash 
cd ~/.la/
```

Склонировать репозиторий в выбранную директорию.

## Зависимости

### Linux packages

```bash
sudo 
```

### Docker

Перед запуском необходимо установить все дополнительные [пакеты](#linux-packages)

- Поднятие docker-compose в фоновом режиме.

```bash
sudo docker-compose -f docker-compose.yaml up -d;
```

- START/STOP Docker контейнера.

```bash
# stop docker
sudo docker-compose stop; 
```

```bash
# start docker
sudo docker-compose start;  
```

- Для удаления Docker контейнера.

```bash
sudo docker-compose down;
```

> Удаление Docker контейнера с удалением `всех` его данных.
> ```bash
> sudo docker-compose down --volumes; 
> ```

### App

- Установка зависимостей приложения.

```bash
pip install -r requirements.txt
```

:arrow_up:[ОГЛАВЛЕНИЕ](#оглавление-page_with_curl)

<hr>

## Настройка приложения

Файл с настройками параметров находится в файле [settings.ini](settings.ini).

```bash
nano ~/.la/app/settings.ini
```

:arrow_up:[ОГЛАВЛЕНИЕ](#оглавление-page_with_curl)

<hr>