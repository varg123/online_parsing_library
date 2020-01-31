import requests

def main():
    resp = requests.get('http://tululu.org/txt.php?id=32168')
    with open('1.txt', 'wb') as file:
        file.write(resp.content)

if __name__ == '__main__':
    main()