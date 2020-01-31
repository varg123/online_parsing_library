import requests
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    cleaned_folder = sanitize_filename(folder)
    cleaned_filename = sanitize_filename(filename)
    if not os.path.exists(cleaned_folder):
        os.makedirs(cleaned_folder)
    responce = requests.get(url)
    book_path = os.path.join(cleaned_folder, f'{cleaned_filename}.txt')
    if 'html' not in responce.headers['Content-Type']:
        with open(book_path, 'wb') as book:
            book.write(responce.content)
            return book_path
    return None


def download_image(url, filename, folder='image/'):
    cleaned_folder = sanitize_filename(folder)
    cleaned_filename = sanitize_filename(filename)
    if not os.path.exists(cleaned_folder):
        os.makedirs(cleaned_folder)
    responce = requests.get(url)
    img_path = os.path.join(cleaned_folder, f'{cleaned_filename}.jpg')
    if 'jpeg' in responce.headers['Content-Type']:
        with open(img_path, 'wb') as img:
            img.write(responce.content)
            return img_path
    return None


def main():
    # # Примеры использования
    # url = 'http://tululu.org/txt.php?id=1'
    #
    # filepath = download_txt(url, 'Алиби')
    # print(filepath)  # Выведется books/Алиби.txt
    #
    # filepath = download_txt(url, 'Али/би', folder='books/')
    # print(filepath)  # Выведется books/Алиби.txt
    #
    # filepath = download_txt(url, 'Али\\би', folder='txt/')
    # print(filepath)  # Выведется txt/Алиби.txt

    # Примеры использования
    url = 'http://tululu.org/shots/9.jpg'

    filepath = download_image(url, 'Алиби')
    print(filepath)


if __name__ == '__main__':
    main()
