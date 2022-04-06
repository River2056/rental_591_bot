import os
import requests
import smtplib
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from email.message import EmailMessage

from playwright.sync_api import sync_playwright
from LinkObject import LinkObject

def write_to_html_file(content):
    if not os.path.exists('./html/'):
        os.mkdir('./html/')

    if not os.path.exists(os.path.join('./html', 'output.html')):
        Path(os.path.join('./html', 'output.html')).touch()

    with open(os.path.join('./html', 'output.html'), 'w', encoding='utf-8') as file:
        file.write(content)

def send_html_mail(msg):
    current_date = datetime.date()
    port = 587
    account = 'tommy0625tung@hotmail.com'
    password = 'tifa2056'

    email = EmailMessage()
    email['Subject'] = f'{current_date} houses for rental'
    email['From'] = 'tommy0625tung@hotmail.com'
    email['To'] = 'chen0625tung@gmail.com'
    email.set_content(msg, subtype='html')

    with smtplib.SMTP('smtp-mail.outlook.com', port) as server:
        server.starttls()
        server.ehlo()
        server.login(account, password)
        server.send_message(email)

def scroll_to_bottom(page):
        page.evaluate('''
            var intervalID = setInterval(function() {
                var scrollingElement = (document.scrollingElement || document.body);
                scrollingElement.scrollTop = scrollingElement.scrollHeight;
            }, 200);
        ''')
        prev_height = None
        while True:
            curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
            if not prev_height:
                prev_height = curr_height
                time.sleep(1)
            elif prev_height == curr_height:
                page.evaluate('clearInterval(intervalID)')
                break
            else:
                prev_height = curr_height
                time.sleep(1)

def fetch_contents(page):
    page.wait_for_selector('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
    rows = page.locator('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
    soup = BeautifulSoup(rows.inner_html(), 'html.parser')
    individual_items = soup.find_all('section', 'vue-list-rent-item')

    result = []
    for item in individual_items:
        link_obj = LinkObject()
        a_link = item.find('a')
        link_obj.link = a_link['href']

        title_tag = item.find('div', 'item-title')
        link_obj.title = title_tag.text

        price_tag = item.find('div', 'item-price-text')
        link_obj.price = price_tag.text

        photos = item.find('ul', 'carousel-list')
        link_obj.photos = []
        imgs = photos.find_all(lambda tag: tag.has_attr('data-original'))
        for img in imgs:
            link_obj.photos.append(img['data-original'])
        result.append(link_obj.to_html())

    return result

def main():
    base_url = 'https://rent.591.com.tw'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url)

        # rent range start
        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)').fill('5000')

        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)').fill('12000')

        page.wait_for_selector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')
        page.locator('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button').click()

        # scroll to bottom to trigger javascript load
        # fetch first 3 pages
        total_results = []
        for i in range(3):
            page.wait_for_load_state()
            scroll_to_bottom(page)
        
            # content list
            page_contents = fetch_contents(page)
            total_results.extend(page_contents)

            # next page
            page.wait_for_selector('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext')
            page.locator('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext').click()
    
        send_html_mail('\n'.join(total_results))
        
if __name__ == '__main__':
    main()
