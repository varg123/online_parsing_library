import requests
import os

HOME_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = os.path.join(HOME_DIR, 'books')


def main():
    os.makedirs(BOOKS_DIR, exist_ok=True)
    for book_id in range(1, 11):
        responce = requests.get(f'http://tululu.org/txt.php?id={book_id}')
        book_path = os.path.join(BOOKS_DIR, f'{book_id}.txt')
        if 'html' not in responce.headers['Content-Type']:
            with open(book_path, 'wb') as book:
                book.write(responce.content)


if __name__ == '__main__':
    main()
