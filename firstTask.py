import requests
import os
from bs4 import BeautifulSoup


def get_urls_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.find_all('a')
    urls = []
    can_save_links = False
    iteration_number = 0
    for link in links:
        if iteration_number == 100:
            return urls
        if link.get('href') == "/2-A":
            can_save_links = True

        if link.get('href') and can_save_links:
            urls.append(link.get('href'))
            iteration_number += 1


def collect_urls(base_url, num_urls):
    collected_urls = []

    url = base_url
    urls_on_page = get_urls_from_page(url)
    print(f" Нашел: {urls_on_page}\n")
    collected_urls.extend(urls_on_page)

    return collected_urls[:num_urls]


base_url = 'https://ozhegov.slovaronline.com'
num_urls_to_collect = 100

collected_urls = collect_urls(base_url, num_urls_to_collect)


def download_page(url, file_number):
    response = requests.get(url)

    if not os.path.exists('downloaded_pages'):
        os.makedirs('downloaded_pages')

    filename = f'downloaded_pages/page_{file_number}.html'
    with open(filename, 'wb') as file:
        file.write(response.content)

    return filename


with open('index.txt', 'w', encoding='utf-8') as index_file:
    for i, url in enumerate(collected_urls, start=1):
        downloaded_file = download_page(base_url + url, i)

        index_file.write(f'{i}: {base_url + url}\n')
