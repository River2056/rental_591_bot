import os
import requests
import smtplib
import time
import schedule
import asyncio
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from email.message import EmailMessage

from pyppeteer import launch
from LinkObject import LinkObject

def send_html_mail(msg):
    current_date = datetime.now().date()
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

            photos = item.find('ul', 'carousel-list')
            link_obj.photos = []
            imgs = photos.find_all(lambda tag: tag.has_attr('data-original'))
            for img in imgs:
                link_obj.photos.append(img['data-original'])
            result.append(link_obj.to_html())

    return result

async def scrap_591_and_send_html_mail():
    base_url = 'https://rent.591.com.tw'
    
    browser = await launch(headless=True, executablePath='/usr/bin/chromium-browser')
    page = await browser.newPage()
    await page.goto(base_url)

    # rent range start
    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)')
    await page.type('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(1)', '5000')

    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)')
    await page.type('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > input:nth-child(3)', '12000')

    page.waitForSelector('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')
    await page.click('#rent-list-app > div > div.vue-filter-container > section:nth-child(3) > ul > li.filter-item-input > div > button')

    # scroll to bottom to trigger javascript load
    # fetch first 3 pages
    total_results = []
    for i in range(3):
        page.waitFor(3000)
        await scroll_to_bottom(page)
    
        # content list
        page_contents = await fetch_contents(page)
        total_results.extend(page_contents)

        # next page
        page.waitForSelector('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext')
        await page.click('#rent-list-app > div > div.list-container-content > div > section.vue-public-list-page > div > a.pageNext')

    send_html_mail('\n'.join(total_results))

def wrapper_func():
    print('running function...')
    print(f'{datetime.now()}')
    asyncio.get_event_loop().run_until_complete(scrap_591_and_send_html_mail())
    print(f'function complete: {datetime.now()}')

def main():
    print('start 591 scrap bot...')
    schedule.every().day.at('05:00').do(wrapper_func)

    while True:
        schedule.run_pending()
        time.sleep(1)
    # asyncio.get_event_loop().run_until_complete(scrap_591_and_send_html_mail())
        
if __name__ == '__main__':
    main()
