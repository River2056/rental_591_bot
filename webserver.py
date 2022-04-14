from flask import Flask
from main import scrap_591_and_send_html_mail

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello World</h1>'

@app.route('/scrap-591')
async def activate_scrap_591_bot():
    print('start scraping...')
    await scrap_591_and_send_html_mail()
    print('Done!')
    return 'Done scraping 591!'

if __name__ == '__main__':
    app.run()
