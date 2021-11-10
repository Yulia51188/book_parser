import argparse
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from book_parser import check_for_redirect

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
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    return soup


def parse_book_urls(soup, root_url):
    book_card_soups = soup.find_all('table', class_='d_book')
    book_urls = [urljoin(root_url, book_soup.find('a')['href'])
                 for book_soup in book_card_soups]
    return book_urls


def parse_some_category_pages(url, count):
    if count == 1:
        page_urls = []
    else:
        page_urls = [urljoin(url, f'{page_index}')
                     for page_index in range(2, count + 1)]
    page_urls.insert(0, url)

    book_urls = []
    for page_url in page_urls:
        soup = fetch_page_soup(page_url)
        book_urls.extend(parse_book_urls(soup, TULULU_URL))
    return book_urls


def main():
    args = parse_arguments()
    book_urls = parse_some_category_pages(args.category_url, args.pages_count)
    for index, url in enumerate(book_urls, start=1):
        print(f'{index}. {url}')


if __name__ == '__main__':
    main()
