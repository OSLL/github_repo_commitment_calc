  # GITLogger

## Установка зависимостей

Для корректной работы приложения необходимо установить зависимости, указанные в `requirements.txt`, чтобы это сделать 
используйте команду:

```commandline
pip install -r requirements.txt
```

## Запуск приложения:
1. Логирование commits
```commandline
python3 main.py [-t, --token] token (github токен вместо token) [-l, --list]  list (list - строка пути к txt файлу со списком репозиториев) [-o, --out] out (out - название csv файла, в который будут помещены все логи) [-b, --branch] branch (branch - название конкретной ветки, откуда брать коммиты или all - логгировать все коммиты изо всех веток)
```
2. Логирование issues
```commandline
python3 main.py -i [-t, --token] token (github токен вместо token) [-l, --list]  list (list - строка пути к txt файлу со списком репозиториев) [-o, --out] out (out - название csv файла, в который будут помещены все логи)
```
3. Логирование pull requests
```commandline
python3 main.py -p [-t, --token] token (github токен вместо token) [-l, --list]  list (list - строка пути к txt файлу со списком репозиториев) [-o, --out] out (out - название csv файла, в который будут помещены все логи)
```
4. Логирование непринятых приглашений в репо
```commandline
python3 main.py --invites [-t, --token] token (github токен вместо token) [-l, --list]  list (list - строка пути к txt файлу со списком репозиториев) [-o, --out] out (out - название csv файла, в который будут помещены все логи)
```



##  Получение токена для работы с Google таблицей:
Сначала нужно создать проект на сайте  [Google Cloud](https://console.cloud.google.com/). Выбираем название проекта, жмем на кнопку "Create".

Затем в меню слева нажимаем на API'S & Services, выбираем Enabled APIs & services. Затем на новой страничке сверху находим "+" с надписью ENABLE APIS AND SERVICES. В поиске находим sheet, нажимаем на кнопку enable, такое же можно сделать и для drive. Теперь приложение может общаться с помощью API Google sheets.

В меню слева в API'S & Services переходим на вкладку Credentials, сверху должен быть восклицательный знак в оранжевом треугольнике, в этом сообщении нажимаем на CONFIGURE CONSENT SCREEN. Выбираем external и жмем Create. Заполняем поля со звездочками, жмем SAVE AND CONTINUE.

Заходим опять в Credentials. Нажимаем сверху на "+" CREATE CREDENTIALS и выбираем Service account. На первом этапе создаем имя,;жмем continue, на втором даем себе права owner, жмем DONE.

В таблице Service Accounts будет запись, нажимаем на нее. Сверху будет вкладка keys. Add key -> Create new key -> json -> create. Получаем нужный json файл.
##  Получение table_id и sheet_id для работы с Google таблицей:
После создания таблицы в google sheets, получаем ссылку на эту таблицу и вводим ее в любом поисковике.В получившемся запросе после строчки "d/" будет находиться table_id, после строчки "gid=" будет находиться sheet_id 
## Экспорт таблицы в Google Sheets:

``` commandline
python3 main.py -p [-t, --token] token (github токен вместо token) [-l,--list] list (list - строка пути к txt файлу со списком репозиториев) [-o, --out] out (out - название csv файла, в который будут помещены все логи) [--google_token] token.json (файл с google токеном) [--table_id] table_id (id таблицы, указанной в url пути до таблицы) [--sheet_id] sheet_id (id конкретного листа в таблице google)
```

## Файл со списком репозиториев:

Репозитории хранятся в txt файле. Каждый репозиторий записывается в отдельную строку.
Должно быть указано полное имя репозитория. (Название организации/название репозитория)
