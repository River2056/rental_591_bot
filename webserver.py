from flask import Flask
from flask import request
from main import scrap_591_and_send_html_mail

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<h1>Hello World</h1>"


@app.route("/scrap-591")
async def activate_scrap_591_bot():
    print("start scraping...")
    args_min = request.args.get("min")
    args_max = request.args.get("max")
    min = str(args_min) if args_min and str(args_min) != "None" else "0"
    max = str(args_max) if args_max and str(args_max) != "None" else "0"
    send_mail = bool(request.args.get("mail"))
    print(f"min: {min}, max: {max}, send_mail: {send_mail}")
    result = await scrap_591_and_send_html_mail(min, max, send_mail)
    print("Done!")
    return "\n".join(result)


if __name__ == "__main__":
    app.run()
