import logging
import os
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def load_book(book_id, url='https://tululu.org/txt.php'):
    params = {'id': book_id}

    response = requests.get(url, params=params, allow_redirects=False)
    response.raise_for_status()  
    check_for_redirect(response)
    return response.text


def save_book(book_id, text):
    os.makedirs('books', exist_ok=True)
    file_path = os.path.join('books', f'{book_id}.txt') 

    with open(file_path, 'w') as file_obj:
        file_obj.write(text)


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError('Failed to load book: redirect detected '
                                 f'for url {response.url}''')


def main():
    for index in range(1, 11):
        try:
            book_text = load_book(index)
            save_book(index, book_text)
            logger.info(f'Save book {index}')
        except requests.HTTPError as error:
            logger.error(error)


if __name__ == '__main__':
    main()
