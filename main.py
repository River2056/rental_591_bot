import os
import re
import sys
import time
import yaml
import asyncio
import smtplib
import requests
import schedule
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from email.message import EmailMessage

from pyppeteer import launch
from LinkObject import LinkObject

def read_config():
    if not os.path.exists(os.path.join('config', 'config.yaml')):
        print('config file not found! please provide config.yaml')
        sys.exit(1)

    with open(os.path.join('config', 'config.yaml')) as file:
        config = yaml.safe_load(file.read())
        return config

def send_html_mail(msg, username, password, to_username):
    current_date = datetime.now().date()
    port = 587
    account = username
    password = password

    email = EmailMessage()
    email['Subject'] = f'{current_date} houses for rental'
    email['From'] = username
    email['To'] = to_username
    email.set_content(msg, subtype='html')

    with smtplib.SMTP('smtp-mail.outlook.com', port) as server:
        server.starttls()
        server.ehlo()
        server.login(account, password)
        server.send_message(email)

async def scroll_to_bottom(page):
        await page.evaluate('''
            var intervalID = setInterval(function() {
                var scrollingElement = (document.scrollingElement || document.body);
                scrollingElement.scrollTop = scrollingElement.scrollHeight;
            }, 200);
        ''')
        prev_height = None
        while True:
            curr_height = await page.evaluate('(window.innerHeight + window.scrollY)')
            if not prev_height:
                prev_height = curr_height
                time.sleep(1)
            elif prev_height == curr_height:
                await page.evaluate('clearInterval(intervalID)')
                break
            else:
                prev_height = curr_height
                time.sleep(1)

async def fetch_contents(page):
    page.waitForSelector('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
    element_handles = await page.JJ('#rent-list-app > div > div.list-container-content > div > section.vue-list-rent-content')
    result = []
    for handle in element_handles:
        inner_html = await (await handle.getProperty('innerHTML')).jsonValue()
        soup = BeautifulSoup(inner_html, 'html.parser')
        individual_items = soup.find_all('section', 'vue-list-rent-item')

        for item in individual_items:
            link_obj = LinkObject()
            a_link = item.find('a')
            link_obj.link = a_link['href']

            title_tag = item.find('div', 'item-title')
            link_obj.title = title_tag.text

            price_tag = item.find('div', 'item-price-text')
            link_obj.price = price_tag.text
            price_tag_int = int(re.sub(r'\W', '', price_tag.text)[:-2])
            link_obj.price_int = price_tag_int

            photos = item.find('ul', 'carousel-list')
            link_obj.photos = []
            imgs = photos.find_all(lambda tag: tag.has_attr('data-original'))
            for img in imgs:
                link_obj.photos.append(img['data-original'])
            result.append(link_obj)

    return result

async def scrap_591_and_send_html_mail():
    base_url = 'https://rent.591.com.tw'
    config = read_config()
    
    browser = await launch(headless=True, executablePath='/usr/bin/chromium-browser')
    page = await browser.newPage()
    await page.goto(base_url)

    # rent range start
    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)')
    await page.type('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)', str(config['range-start']))

    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)')
    await page.type('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)', str(config['range-end']))

    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')
    await page.click('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')

    # scroll to bottom to trigger javascript load
    # fetch first 3 pages
    total_results = []
    element_count = config['element-count']
    while len(total_results) < element_count:
        page.waitFor(3000)
        await scroll_to_bottom(page)
    
        # content list
        page_contents = await fetch_contents(page)
        page_contents = list(filter(lambda x: x.price_int <= config['range-end'], page_contents))
        total_results.extend(page_contents)

        # next page
        page.waitForSelector('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext')
        await page.click('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext')
    
    total_results = list(map(lambda x: x.to_html(), total_results))
    send_html_mail('\n'.join(total_results), config['email']['from']['username'], config['email']['from']['password'], config['email']['to']['username'])

def wrapper_func():
    print('running function...')
    print(f'{datetime.now()}')
    asyncio.get_event_loop().run_until_complete(scrap_591_and_send_html_mail())
    print(f'function complete: {datetime.now()}')

def main():
    # print('start 591 scrap bot...')
    # schedule.every().day.at('05:00').do(wrapper_func)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    asyncio.get_event_loop().run_until_complete(scrap_591_and_send_html_mail())
        
if __name__ == '__main__':
    main()
