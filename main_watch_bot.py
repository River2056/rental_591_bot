import os
import requests
import smtplib
import ssl
import schedule
import time
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
from email.mime.text import MIMEText

from LinkObject import LinkObject
from constants import BASE_URL
from constants import HOME

def write_to_html_file(content):
    if not os.path.exists('./html/'):
        os.mkdir('./html/')

    if not os.path.exists(os.path.join('./html', 'output.html')):
        Path(os.path.join('./html', 'output.html')).touch()

    with open(os.path.join('./html', 'output.html'), 'w', encoding='utf-8') as file:
        file.write(content)

def sort_according_to_date(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[-1]
    i, j = -1, 0
    for e in range(len(arr)):
        if datetime.strptime(arr[e].time, '%Y-%m-%d') > datetime.strptime(pivot.time, '%Y-%m-%d'):
            i += 1
            tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp
        j += 1
    i += 1
    tmp = arr[i]
    arr[i] = pivot
    arr[-1] = tmp

    left = sort_according_to_date(arr[0:i])
    mid = arr[i:i+1]
    right = sort_according_to_date(arr[i+1:])
    return left + mid + right


def parse_html_into_obj(base_url, res):
    soup = BeautifulSoup(res.text, 'html.parser')
    list_a = soup.find_all('div', 'list A')
    list_b = soup.find_all('div', 'list B')

    raw_data = list_a + list_b
    result = []
    for data in raw_data:
        a_link = data.find('a')
        href_link = a_link['href']
        full_link = f'{base_url}{href_link}'
        
        title = [span for span in a_link.find('span', 'stitle')][0]
        date = [span for span in a_link.find('span', 'date')][0]
        linkObject = LinkObject(title=title, link=full_link, time=date)
        result.append(linkObject)

    result = sort_according_to_date(result)
    return result

def send_email(subject, message, destination):
    msg = MIMEText(message, 'plain')
    msg['Subject'] = subject

    # login
    port = 587
    account = 'tommy0625tung@hotmail.com'
    password = 'tifa2056'

    with smtplib.SMTP('smtp.office365.com', port) as server:
        server.starttls()
        server.ehlo()
        server.login(account, password)
        server.sendmail(account, destination, msg.as_string())

def send_watch_result_through_mail():
    res = requests.get(f'{BASE_URL}{HOME}')
    notices = '\n\n'.join([str(obj) for obj in parse_html_into_obj(BASE_URL, res)])
    now = datetime.now()
    current_date = now.date()

    print(notices)
    subject = f'{current_date} rental watch result'
    message = notices

    send_email(subject, message, 'chen0625tung@gmail.com')
    print('Done sending!')
    print(f'finished time: {now}')

def main():
    print('starting rental watch bot...')
    # schedule.every().day.at('8:00').do(send_watch_result_through_mail)
    schedule.every().day.at('12:00').do(send_watch_result_through_mail)
    # schedule.every().day.at('17:00').do(send_watch_result_through_mail)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
    # send_watch_result_through_mail()
