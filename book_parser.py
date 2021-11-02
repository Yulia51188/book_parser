import logging
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
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


def parse_book_info(book_id, url_template='https://tululu.org/b{book_id}/'):
    response = requests.get(url_template.format(book_id=book_id))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_header = soup.find('div', id='content').find('h1')
    title, author = book_header.text.split('::')

    book_info = {
        'id': book_id,
        'title': title.strip(),
        'author': author.strip(),
    }

    return book_info


def save_book(book_id, title, text, folder='books'):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(
        folder,
        sanitize_filename(f'{book_id}. {title}.txt')
    ) 

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
            book_info = parse_book_info(index)

            save_book(index, book_info['title'], book_text)
            logger.info(f'Save book {book_info["title"]} by'
                        f'{book_info["author"]} with ID {index}')
        except requests.HTTPError as error:
            logger.error(error)


if __name__ == '__main__':
    main()
