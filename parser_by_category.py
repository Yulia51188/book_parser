import argparse
import json
import logging
import os
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import book_parser

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
        '-s', '--start_page',
        type=int,
        default=1,
        help='start page index to parse, default is 1',
    )
    parser.add_argument(
        '-e', '--end_page',
        type=int,
        help='number of pages to parse',
    )

    parser.add_argument(
        '-si', '--skip_images',
        action='store_true',
        help="if set - the script doesn't download book cover images"
    )
    parser.add_argument(
        '-st', '--skip_txt',
        action='store_true',
        help="if set - the script doesn't download book txt files"
    )

    parser.add_argument(
        '--json_path',
        type=str,
        help='path to save JSON file with downloaded books info',
    )
    parser.add_argument(
        '--dest_folder',
        type=str,
        help='path to save downloaded files (txt files, covers, book info)',        
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
    book_urls_selector = '.ow_px_td table.d_book .bookimage a:first-child'
    book_links = soup.select(book_urls_selector) 

    book_urls = [urljoin(root_url, link_tag['href'])
                 for link_tag in book_links]
    return book_urls


def parse_max_page(category_url):
    soup = fetch_page_soup(category_url)

    max_page_selector = 'p.center a.npage:last-child'
    max_page = soup.select_one(max_page_selector)
    return int(max_page.text)


def collect_book_urls_by_category(category_url, start_page, end_page):
    max_page_index = parse_max_page(category_url)

    if start_page > max_page_index:
        raise ValueError(f'Only {max_page_index} pages are found. '
                         'Restart and input correct page indexes')

    if not end_page or end_page > max_page_index:
        end_page = max_page_index
        logger.warning('Correct input end page index to maximum available - '
                       f'{end_page}')

    page_urls = [urljoin(category_url, str(page_index))
                 for page_index in range(start_page, end_page + 1)]    

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


def download_books_by_urls(book_urls, skip_txt, skip_images, folder_path):
    book_ids = [get_book_id_from_url(url) for url in book_urls]

    if folder_path and not(skip_txt and skip_images):
        os.makedirs(folder_path, exist_ok=True)

    library = []
    books_count = len(book_ids)
    for index, book_id in enumerate(book_ids, start=1):
        try:
            book_text = book_parser.load_book(book_id)
            book_info = book_parser.parse_book_info(book_id)
            library.append(book_info)

            if not skip_txt:
                book_parser.save_book(
                    book_id,
                    book_info['title'],
                    book_text,
                    folder_path,
                )
        
            if not skip_images:
                book_parser.download_image(
                    book_id,
                    book_info['image_url'],
                    folder_path,
                )
            
            logger.info(f'Download {book_info["title"]} {index}/{books_count}')            
        except requests.HTTPError as error:
            logger.error(error)
    return library


def save_books_catalogue(books_catalogue, folder_path, filename='library.json'):
    if folder_path:
        os.makedirs(folder_path, exist_ok=True)
        result_path = os.path.join(folder_path, filename)
    else:
        result_path = filename

    with open(result_path, "w") as write_file:
        json.dump(books_catalogue, write_file, ensure_ascii=False, indent=4)    
    return result_path


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    args = parse_arguments()

    if args.start_page < 1:
        args.start_page = 1
        logger.warning('Start page index corrected to 1')
    if args.end_page and args.end_page < args.start_page:
        raise ValueError('Input page indexes range is wrong: '
                         f'from {args.start_page} to {args.end_page}')

    book_urls = collect_book_urls_by_category(
        args.category_url,
        args.start_page,
        args.end_page
    )
    library = download_books_by_urls(
        book_urls,
        args.skip_txt,
        args.skip_images,
        args.dest_folder
    ) 
    
    result_path = save_books_catalogue(library, args.json_path or args.dest_folder)
    logger.info(f'Books info saved as {result_path}')


if __name__ == '__main__':
    main()
