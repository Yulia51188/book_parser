import argparse
import logging
import os
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Download books in TXT format in your home library'
    )
    parser.add_argument(
        'start_index',
        type=int,
        help='start index to download books in book ID range from start to stop',
    )
    parser.add_argument(
        'stop_index',
        type=int,
        help='stop index to download books in book ID range from start to stop'
    )
    return parser.parse_args()


def load_book(book_id, url='https://tululu.org/txt.php'):
    params = {'id': book_id}
    response = requests.get(url, params=params, allow_redirects=False)

    response.raise_for_status()  
    check_for_redirect(response)

    return response.text


def parse_book_page(soup):
    book_header_selector = 'div[id=content] h1'
    book_header_layout = soup.select_one(book_header_selector)
    title, author = book_header_layout.text.split('::')

    book_img_selector = '.bookimage img'
    book_img_layout = soup.select_one(book_img_selector)
    book_img_url = book_img_layout['src']

    comments_selector = 'div.texts span'
    comment_soups = soup.select(comments_selector)
    comments = [comment_layout.text for comment_layout in comment_soups]

    genre_selector = 'span.d_book a'
    genre_layouts = soup.select(genre_selector)
    genres = [genre_layout.text for genre_layout in genre_layouts]

    book_info = {
        'title': title.strip(),
        'author': author.strip(),
        'image_url': book_img_url,
        'comments': comments,
        'genre': genres,
    }

    return book_info


def parse_book_info(book_id, url_template='https://tululu.org/b{book_id}/'):
    response = requests.get(
        url_template.format(book_id=book_id),
        allow_redirects=False
    )
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_info = parse_book_page(soup)

    book_info['id'] = book_id
    book_info['image_url'] = urljoin(response.url, book_info['image_url'])

    return book_info


def get_file_path(root_path, folder_name, filename):
    if root_path:
        os.makedirs(
            os.path.join(root_path, folder_name),
            exist_ok=True
        ) 
        return os.path.join(root_path, folder_name, filename)
    
    os.makedirs(folder_name, exist_ok=True)
    return os.path.join(folder_name, filename)


def save_book(book_id, title, text, root_path, folder_name='books'):
    file_path = get_file_path(
        root_path,
        folder_name,
        sanitize_filename(f'{book_id}. {title}.txt')
    )

    with open(file_path, 'w') as file_obj:
        file_obj.write(text)


def parse_filename(url):
    file_path = unquote(urlparse(url).path)
    return os.path.basename(file_path)


def download_image(book_id, image_url, root_path, folder_name='images'):
    response = requests.get(image_url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)

    file_path = get_file_path(
        root_path,
        folder_name,
        parse_filename(image_url)
    )
    
    with open(file_path, 'wb') as file_obj:
        file_obj.write(response.content)
    return file_path


def check_for_redirect(response):
    if 300 <= response.status_code < 400:
        raise requests.HTTPError('Failed to load book: redirect detected '
                                 f'for url {response.url}''')


def download_books(start_index, stop_index):
    for book_id in range(start_index, stop_index + 1):
        try:
            book_text = load_book(book_id)
            book_info = parse_book_info(book_id)

            logger.info(f'Book {book_info["title"]} genre is {book_info["genre"]}')

            save_book(book_id, book_info['title'], book_text)
            logger.info(f'Save book {book_info["title"]} by '
                        f'{book_info["author"]} with ID {book_id}')
        
            cover_path = download_image(book_id, book_info['image_url'])
            logger.info(f'Save book {book_id} cover to {cover_path}')            
        except requests.HTTPError as error:
            logger.error(error)


def main():
    args = parse_arguments()
    if args.start_index < 1:
        args.start_index = 1
        logger.warning('Start index corrected to 1')
    if args.stop_index < args.start_index:
        raise ValueError('Input indexes range is wrong: '
                         f'from {args.start_index} to {args.stop_index}')
    download_books(args.start_index, args.stop_index)


if __name__ == '__main__':
    main()
