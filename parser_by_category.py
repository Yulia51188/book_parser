import argparse
import json
import logging
from urllib.parse import urljoin, unquote, urlparse

import requests
from bs4 import BeautifulSoup

import book_parser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TULULU_URL = 'https://tululu.org/'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=('Download books in TXT format for your home library from'
                     'tululu genre page given as url')
    )
    parser.add_argument(
        'category_url',
        type=str,
        help='genre (category) page url',
    )
    parser.add_argument(
        '-p', '--pages_count',
        type=int,
        default=4,
        help='number of pages to parse',
    )
    return parser.parse_args()


def fetch_page_soup(url):
    response = requests.get(
        url,
        allow_redirects=False
    )
    response.raise_for_status()
    book_parser.check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    return soup


def parse_book_urls(soup, root_url):
    book_card_soups = soup.find_all('table', class_='d_book')
    book_urls = [urljoin(root_url, book_soup.find('a')['href'])
                 for book_soup in book_card_soups]
    return book_urls


def parse_some_category_pages(category_url, count):
    if count == 1:
        page_urls = []
    else:
        page_urls = [urljoin(category_url, f'{page_index}')
                     for page_index in range(2, count + 1)]
    page_urls.insert(0, category_url)

    book_urls = []
    for page_url in page_urls:
        soup = fetch_page_soup(page_url)
        book_urls.extend(parse_book_urls(soup, TULULU_URL))
    return book_urls


def get_book_id_from_url(url):
    id_string = unquote(urlparse(url).path)
    book_id = (
        id_string
        .replace('/', '')
        .replace('b', '')
    )
    return book_id


def download_books_by_urls(book_urls):
    book_ids = [get_book_id_from_url(url) for url in book_urls]

    library = []
    for index, book_id in enumerate(book_ids, start=1):
        try:
            book_text = book_parser.load_book(book_id)
            book_info = book_parser.parse_book_info(book_id)
            library.append(book_info)

            book_parser.save_book(book_id, book_info['title'], book_text)
        
            book_parser.download_image(
                book_id,
                book_info['image_url']
            )
            logger.info(f'Download {book_info["title"]} {index}/{len(book_ids)}')            
        except requests.HTTPError as error:
            logger.error(error)
    return library


def main():
    args = parse_arguments()

    book_urls = parse_some_category_pages(args.category_url, args.pages_count)
    library = download_books_by_urls(book_urls)

    with open("library.json", "w") as write_file:
        json.dump(library, write_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
