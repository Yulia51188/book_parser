import logging
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import requests
from urllib.parse import unquote, urljoin, urlparse

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

    book_header_layout = soup.find('div', id='content').find('h1')
    title, author = book_header_layout.text.split('::')

    book_img_layout = soup.find('div', class_='bookimage').find('img')
    book_img_url = book_img_layout['src']

    comment_soups = soup.find_all('div', class_='texts')
    comments = [comment_layout.find('span').text 
                for comment_layout in comment_soups]

    genre_layout = soup.find('span', class_='d_book').find('a')
    genre = genre_layout.text

    book_info = {
        'id': book_id,
        'title': title.strip(),
        'author': author.strip(),
        'image_url': urljoin(response.url, book_img_url),
        'comments': comments,
        'genre': genre,
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


def save_comments(book_info, folder='comments'):
    if not any(book_info['comments']):
        return None

    os.makedirs(folder, exist_ok=True)
    filename_template = 'Комментарии к {id}.{title}.txt'
    file_path = os.path.join(
        folder,
        sanitize_filename(filename_template.format(
            id=book_info['id'],
            title=book_info['title'],
        ))
    )

    with open(file_path, 'w') as file_obj:
        file_obj.write('\n\n'.join(book_info['comments']))
    return file_path


def parse_filename(url):
    file_path = unquote(urlparse(url).path)
    return os.path.basename(file_path)


def download_image(book_id, image_url, folder='images'):
    response = requests.get(image_url)
    response.raise_for_status()

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(
        folder,
        parse_filename(image_url)
    ) 

    with open(file_path, 'wb') as file_obj:
        file_obj.write(response.content)
    return file_path


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.HTTPError('Failed to load book: redirect detected '
                                 f'for url {response.url}''')


def main():
    for index in range(1, 11):
        try:
            book_text = load_book(index)
            book_info = parse_book_info(index)

            logger.info(f'Book {book_info["title"]} genre is {book_info["genre"]}')
            
            save_book(index, book_info['title'], book_text)
            logger.info(f'Save book {book_info["title"]} by '
                        f'{book_info["author"]} with ID {index}')

            comment_path = save_comments(book_info)
            if comment_path:
                logger.info(f'Save book {index} comments to {comment_path}') 
            
            cover_path = download_image(index, book_info['image_url'])
            logger.info(f'Save book {index} cover to {cover_path}')            
        except requests.HTTPError as error:
            logger.error(error)


if __name__ == '__main__':
    main()
