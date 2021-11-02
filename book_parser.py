import os
import requests


def load_book(book_id, url='https://tululu.org/txt.php'):
    params = {'id': book_id}

    response = requests.get(url, params=params)
    response.raise_for_status()  
    return response.text  


def save_book(book_id, text):
    os.makedirs('books', exist_ok=True)
    file_path = os.path.join('books', f'{book_id}.txt') 

    with open(file_path, 'w') as file_obj:
        file_obj.write(text)


def main():
    for index in range(1, 10):
        book_text = load_book(index)
        save_book(index, book_text)


if __name__ == '__main__':
    main()
