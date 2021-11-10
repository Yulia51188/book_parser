import argparse
import logging
import os
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

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
    book_url_soup = soup.find('table', class_='d_book').find('a')
    return urljoin(root_url, book_url_soup['href'])


def main():
    args = parse_arguments()
    print(args.category_url)
    soup = fetch_page_soup(args.category_url)
    print(parse_book_urls(soup, TULULU_URL))


if __name__ == '__main__':
    main()
