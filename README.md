# Парсер книг с сайта tululu.org

Скрипт `book_parser.py` позволяет скачивать с сайта [Tululu](https://tululu.org) книги в заданном диапазоне индексов в формате TXT. Кроме текстов загружаются обложки и комментарии к книгам.

## Как установить

- Для работы со скриптом необходим [Python](https://www.python.org/downloads/) версии 3.7+ и менеджер пакетов `pip`.

- Установите зависимости:
```bash
$ pip install -r requirements.txt
```

## Аргументы

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

## Пример запуска

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

## Выходные данные

Скрипт создаст 3 папки:
- `books` - содержит тексты книг в формате TXT
- `images` - содержит изображения обложек книг
- `comments` - содержит текстовые файлы с комментариями к книгам

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков dvmn.org.
