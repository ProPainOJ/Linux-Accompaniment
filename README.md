# <center>Linux-Accompaniment</center>

<span style="color: white; font-size: 20px;">_Программа для вывода напоминаний, логирования времени работы и другого
вспомогательного
функционала работы в
linux._</span>

# Оглавление 📃

1. [Установка](#span-stylecolorgreenустановка-span)
2. [Зависимости](#brзависимости-)
    - [Linux packages](#brulinux-packagesu-)
    - [Docker](#brudockeru-)
    - [App](#bruappu-)
3. [Настройка приложения](#brнастройка-приложения-)

## <br>*Установка приложения* [🔝](#оглавление-)

<hr>

Перейти в директорию для установки.

```bash 
cd ~/.la/
```

Склонировать репозиторий в выбранную директорию.

## <br>**Зависимости** [🔝](#оглавление-)

<hr>

### <br>*<u>Linux packages</u>* [🔝](#оглавление-)

##### <span style='color:green'>Установка 🟢</span>

```bash
sudo apt-get install scrot python3-tk python3-dev zenity python3-pip
```

##### <span style='color:red'>Удаление 🔴</span>

```bash
sudo apt-get install scrot python3-tk python3-dev zenity python3-pip
```

### <br>*<u>Docker</u>* [🔝](#оглавление-)

##### <span style='color:green'>Установка 🟢</span>

Перед запуском необходимо установить все дополнительные [пакеты](#brulinux-packagesu-)

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

##### <span style='color:red'>Удаление 🔴</span>

```bash
sudo docker-compose down;
```

> Удаление Docker контейнера с удалением `всех` данных в бд.
> ```bash
> sudo docker-compose down --volumes; 
> ```

### <br>*<u>App</u>* [🔝](#оглавление-)

##### <span style='color:green'>Установка 🟢</span>

```bash
pip install -r requirements.txt
```

##### <span style='color:red'>Удаление 🔴</span>

```bash
pip freeze | xargs pip uninstall -y 
```

## <br>**Настройка приложения** [🔝](#оглавление-)

Файл с настройками параметров находится в файле [settings.ini](settings.ini).

```bash
nano ~/.la/app/settings.ini
```

