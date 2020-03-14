import re

import requests
import os
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from pathvalidate.argparse import sanitize_filename_arg, sanitize_filepath_arg
from urllib.parse import urljoin
import argparse
import json
from os.path import join

SITE_URL = 'http://tululu.org/'
IMG_FOLDER = 'images'
TXT_FOLDER = 'books'
JSON_PATH = ''


def check_extension_img_or_gif(response, cleaned_filename):
    if 'gif' in response.headers['Content-Type']:
        return 'nopic.gif'
    elif 'jpeg' in response.headers['Content-Type']:
        return f'{cleaned_filename}.jpg'


def check_extension_txt(response, cleaned_filename):
    if 'text/plain' in response.headers['Content-Type']:
        return f'{cleaned_filename}.txt'


def download_file(url, folder, filename=None, check_extension_function=None):
    if not filename:
        url_re_tmpl = r'http:\/\/[A-Za-z\/\.]*\/([A-Za-z0-9]+)[\.A-Za-z0-9]*'
        filename = re.search(url_re_tmpl, url).group(1)
    cleaned_folder = sanitize_filepath(folder)
    cleaned_filename = sanitize_filename(filename)
    os.makedirs(cleaned_folder, exist_ok=True)
    response = requests.get(url)

    if check_extension_function:
        cleaned_filename = check_extension_function(response, cleaned_filename)

    if cleaned_filename:
        file_path = os.path.join(cleaned_folder, cleaned_filename)
    else:
        return None

    with open(file_path, 'wb') as file:
        file.write(response.content)
        return file_path


def get_book_info(url):
    responce = requests.get(url)
    responce.raise_for_status()
    soup = BeautifulSoup(responce.text, 'lxml')
    bread_crumbs_tag = soup.select_one('#content h1')
    title_book, author_book = bread_crumbs_tag.text.split(' \xa0 :: \xa0 ')

    txt_href_tag = soup.select_one('.d_book tr:nth-of-type(4) a:nth-of-type(2)')
    clean_txt_href = None
    if txt_href_tag:
        clean_txt_href = urljoin(SITE_URL, txt_href_tag.get('href'))

    img_src_tag = soup.select_one('.bookimage a img')
    clean_img_src = None
    if img_src_tag:
        clean_img_src = urljoin(SITE_URL, img_src_tag.get('src'))

    comments_tags = soup.select('.texts span')
    comments = []
    for comment_tag in comments_tags:
        comments.append(comment_tag.text)

    genres_tags = soup.select('span.d_book a')
    genres = []
    for genres_tag in genres_tags:
        genres.append(genres_tag.text)

    return {
        'title': title_book,
        'author': author_book,
        'image': clean_img_src,
        'book_txt': clean_txt_href,
        'comments': comments,
        'genres': genres,
    }


def get_books_urls(start_page_number, end_page_number):
    start_page_url = f'{SITE_URL}/l55/{start_page_number}/'
    resp = requests.get(start_page_url)
    soup = BeautifulSoup(resp.text, 'lxml')
    max_page_number = int(soup.select('.npage')[-1].text)
    for page_numb in range(start_page_number, end_page_number + 1):
        if page_numb > max_page_number:
            return
        url = f'{SITE_URL}/l55/{page_numb}/'
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'lxml')
        a_tags = soup.select('#content tr:nth-of-type(6n+1) a')
        for a_tag in a_tags:
            a_href = a_tag.get('href')
            if a_href:
                yield urljoin(SITE_URL, a_href)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', type=int, default=1)
    parser.add_argument('--end_page', type=int, default=2)
    parser.add_argument('--skip_imgs', type=bool, default=False)
    parser.add_argument('--skip_txt', type=bool, default=False)
    parser.add_argument('--dest_folder', type=sanitize_filepath_arg, default='')
    parser.add_argument('--json_path', type=sanitize_filepath_arg, default='')
    args = parser.parse_args()

    global IMG_FOLDER
    global TXT_FOLDER
    IMG_FOLDER = join(args.dest_folder, IMG_FOLDER)
    TXT_FOLDER = join(args.dest_folder, TXT_FOLDER)
    global JSON_PATH
    JSON_PATH = join(args.json_path, JSON_PATH)

    books_info = []
    for book_url in get_books_urls(
            start_page_number=args.start_page,
            end_page_number=args.end_page):
        book_info = get_book_info(book_url)
        if not book_info:
            continue

        if not args.skip_imgs and book_info.get('image'):
            image_dest = download_file(
                book_info.get('image'),
                IMG_FOLDER,
                check_extension_function=check_extension_img_or_gif
            )
            book_info.update(
                {
                    'image': image_dest
                }
            )

        if not args.skip_txt and book_info.get('book_txt'):
            txt_dest = download_file(
                book_info.get('book_txt'),
                TXT_FOLDER,
                book_info.get('title'),
                check_extension_txt
            )
            book_info.update(
                {
                    'book_txt': txt_dest
                }
            )
        books_info.append(book_info)

    if JSON_PATH:
        os.makedirs(JSON_PATH, exist_ok=True)
    JSON_PATH = join(JSON_PATH, 'books_info.json')
    with open(JSON_PATH, 'wt', encoding='utf8') as books_info_file:
        json.dump(books_info, books_info_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
