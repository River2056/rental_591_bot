import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright

def write_to_html_file(content):
    if not os.path.exists('./html/'):
        os.mkdir('./html/')

    if not os.path.exists(os.path.join('./html', 'output.html')):
        Path(os.path.join('./html', 'output.html')).touch()

    with open(os.path.join('./html', 'output.html'), 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    # document.querySelector("#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content")
    base_url = 'https://rent.591.com.tw'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(base_url)

        # rent range start
        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)').fill('5000')

        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)').fill('12000')

        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button').click()

        # content list
        page.wait_for_selector('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
        rows = page.locator('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
        soup = BeautifulSoup(rows.inner_html(), 'html.parser')
        individual_items = soup.find_all('section', 'vue-list-rent-item')

        for item in individual_items:
            photos = item.find('ul', 'carousel-list')
            imgs = photos.find_all(lambda tag: tag.has_attr('data-original'))
            for img in imgs:
                print(img['data-original'])
        
        page.wait_for_timeout(20000)
    
if __name__ == '__main__':
    main()
