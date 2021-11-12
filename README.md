# Парсер книг с сайта tululu.org

Парсер включает два скрипта, позволяющие скачивать книги в разных режимах:
- `book_parser.py` - позволяет скачивать с сайта [Tululu](https://tululu.org) книги в заданном диапазоне индексов (ID) в формате TXT. Кроме текстов загружаются обложки и комментарии к книгам.
- `parser_by_category.py` - принимает ссылку на страницу жанра, например, [Научная фантастика](https://tululu.org/l55/) и скачивает книги указанного диапазона страниц, а также с другими настройками, описанными ниже.

## Как установить

- Для работы со скриптом необходим [Python](https://www.python.org/downloads/) версии 3.7+ и менеджер пакетов `pip`.

- Установите зависимости:
```bash
$ pip install -r requirements.txt
```

## Скачиваний книг по ID

### Аргументы

Скрипт при запуске требует ввода двух обязательных аргументов:
- `start_index`
- `stop_index`

Значения являются натуральными числами и указывают скрипту диапазон индексов книг для скачивания.

Если `start_index` меньше единицы, то его значение будет изменено на `1`. Если индекс конца диапазона меньше индекса начала, то скрипт завершит работу с ошибкой:

```
Traceback (most recent call last):
  File "book_parser.py", line 170, in <module>
    main()
  File "book_parser.py", line 164, in main
    raise ValueError('Input indexes range is wrong: '
ValueError: Input indexes range is wrong: from 20 to 10
```

### Пример запуска

Запустите скрипт и в увидите в консоли сообщения о ходе загрузки:
```
$ python book_parser.py 2 15
2021-11-03 08:01:14,396 - __main__ - ERROR - Failed to load book: redirect detected for url https://tululu.org/txt.php?id=2
2021-11-03 08:01:14,844 - __main__ - INFO - Book Азбука экономики genre is Деловая литература
2021-11-03 08:01:14,846 - __main__ - INFO - Save book Азбука экономики by Строуп Р with ID 3
2021-11-03 08:01:14,915 - __main__ - INFO - Save book 3 cover to images/nopic.gif
2021-11-03 08:01:15,713 - __main__ - INFO - Book Азиатский способ производства и Азиатский социализм genre is Деловая литература
2021-11-03 08:01:15,714 - __main__ - INFO - Save book Азиатский способ производства и Азиатский социализм by Прохоренко Иван Денисович with ID 4
2021-11-03 08:01:15,756 - __main__ - INFO - Save book 4 cover to images/nopic.gif
2021-11-03 08:01:16,668 - __main__ - INFO - Book Бал хищников genre is Биографии и мемуары
2021-11-03 08:01:16,684 - __main__ - INFO - Save book Бал хищников by Брук Конни with ID 5
2021-11-03 08:01:16,684 - __main__ - INFO - Save book 5 comments to comments/Комментарии к 5.Бал хищников.txt
2021-11-03 08:01:16,725 - __main__ - INFO - Save book 5 cover to images/5.jpg
```

### Выходные данные

Скрипт создаст 3 папки:
- `books` - содержит тексты книг в формате TXT
- `images` - содержит изображения обложек книг
- `comments` - содержит текстовые файлы с комментариями к книгам

## Скачиваний книг со страницы жанра

### Аргументы

Скрипт при запуске требует ввода одного обязательного аргумента:
- `category_url`
Это URL адрес страницы жанра, на которой размещены ссылки на книги. 

При запуске доступны следующие необязательные аргументы:
- `--start_page` - индекс страницы, с которой начать скачивание книг жанра по умолчанию - 1
  - если значение меньше 1, то присваивается значение 1 
  - если значение больше максимального номера страницы, то скрипт завершает работу с ошибкой `ValueError`
- `--end_page` - индекс последней страницы из тех, с которых нужно спарсить книги и скачать
  - если значение больше максимальной страницы, то значение изменяется на максимальное
- `--skip_images` - не скачивать изображения
- `--skip_txt` - не скачивать текстовые файлы
- `--json_path` - указать папку для сохранения JSON файла с информацией о книгах
- `--dest_folder` - указать папку для сохранения скачанных книг, изображений обложек и JSON файла с информацией о книгах (если не указан `json_path`)

Описание доступных настроек можно посмотреть, вызвав команду:
```bash
$ python parser_by_category.py --help
usage: parser_by_category.py [-h] [-s START_PAGE] [-e END_PAGE] [-si] [-st] [--json_path JSON_PATH] [--dest_folder DEST_FOLDER] category_url

Download books in TXT format for your home library from tululu genre page given as url

positional arguments:
  category_url          genre (category) page url

optional arguments:
  -h, --help            show this help message and exit
  -s START_PAGE, --start_page START_PAGE
                        start page index to parse, default is 1
  -e END_PAGE, --end_page END_PAGE
                        number of pages to parse
  -si, --skip_images    if set - the script doesn't download book cover images
  -st, --skip_txt       if set - the script doesn't download book txt files
  --json_path JSON_PATH
                        path to save JSON file with downloaded books info
  --dest_folder DEST_FOLDER
                        path to save downloaded files (txt files, covers, book info)

```

### Примеры запуска

Запустите скрипт и в увидите в консоли сообщения о ходе загрузки:

```bash
$ python parser_by_category.py https://tululu.org/l55/ -s 3 -e 3 -si --dest_folder results_0
2021-11-11 16:01:27,427 - __main__ - INFO - Download 9-я книга. Тарат Зурбин 1/25
...
2021-11-11 16:01:35,724 - __main__ - INFO - Download А вдруг они победят 25/25
2021-11-11 16:01:35,725 - __main__ - INFO - Books info saved as results_0/library.json

```

```bash
$ python parser_by_category.py https://tululu.org/l55/ -e 1 -si -st
2021-11-11 15:40:08,058 - __main__ - INFO - Download Алиби 1/25
...
2021-11-11 15:40:20,066 - __main__ - INFO - Download Общая теория Доминант 25/25
2021-11-11 15:40:20,067 - __main__ - INFO - Books info saved as library.json

```

```bash
$ python parser_by_category.py https://tululu.org/l55/ -s 700 -e 702
2021-11-11 15:08:59,652 - __main__ - WARNING - Correct input end page index to maximum available - 701
2021-11-11 15:09:00,756 - __main__ - INFO - Download Деревня Медный ковш 1/37
2021-11-11 15:09:00,831 - __main__ - ERROR - Failed to load book: redirect detected for url https://tululu.org/txt.php?id=59678
...

```

### Выходные данные

Скрипт создаст:
- папку `books` - содержит тексты книг в формате TXT
- папку `images` - содержит изображения обложек книг
- файл `library.json` - содержит информацию о всех скачанных книгах в JSON формате

Пример содержания `library.json`:
```
[
    {
        "title": "9-я книга. Тарат Зурбин",
        "author": "Карр Алекс",
        "image_url": "https://tululu.org/images/nopic.gif",
        "comments": [],
        "genre": [
            "Научная фантастика"
        ],
        "id": "18943"
    },
    {
        "title": "90х60х90",
        "author": "Берендеев Кирилл",
        "image_url": "https://tululu.org/images/nopic.gif",
        "comments": [
            "Ни фантастики, ни фэнтези, обычный детектив... Про обычную жизненную ситуацию... Правда, пара диалогов заставили задуматься, но не более..."
        ],
        "genre": [
            "Научная фантастика"
        ],
        "id": "18944"
    },
]
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.
