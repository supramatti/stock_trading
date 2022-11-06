import numpy
import requests
from twilio.rest import Client
import os
import datetime
import html

account_sid = os.environ['MY_SID']
auth_token = os.environ['MY_AUTH']

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_api = os.environ['MY_STOCK_API']
news_api = os.environ['MY_NEWS_API']
my_phone = os.environ['MY_PHONE']
my_send_phone = os.environ['MY_SEND_PHONE']

close_data = datetime.date.today() - datetime.timedelta(days=3)
open_data = datetime.date.today() - datetime.timedelta(days=2)

stock_parameters = {
    "symbol": STOCK,
    "function": "TIME_SERIES_DAILY",
    "interval": "5min",
    "apikey": stock_api,
}
news_parameters = {
    "q": COMPANY_NAME,
    "from": open_data,
    "sortby": "popularity",
    "apikey": news_api,
}


def get_stock_data():
    stock_response = requests.get(url="https://www.alphavantage.co/query", params=stock_parameters)
    stock_response.raise_for_status()
    stock_data = stock_response.json()
    close_price = numpy.float64(stock_data['Time Series (Daily)'][str(open_data)]['4. close'])
    open_price = numpy.float64(stock_data['Time Series (Daily)'][str(close_data)]['1. open'])
    difference = abs(open_price - close_price)
    percentage_difference = round((difference / close_price) * 100, 2)
    if percentage_difference > 1:
        send_message("TSLA 10% difference", "Should check")
        get_news()


def get_news():
    news_response = requests.get(url="https://newsapi.org/v2/everything", params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()
    for i in range(3):
        if news_data['totalResults'] >= i:
            msg_title = news_data['articles'][i]['title']
            msg_title = html.unescape(msg_title)
            msg_description = news_data['articles'][i]['description']
            msg_description = html.unescape(msg_description)
            send_message(msg_title, msg_description)


def send_message(title, description):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"{title}\n{description} ",
        from_=my_send_phone,
        to=my_phone,
    )


if open_data.weekday() != 5 and open_data.weekday() != 6:
    if open_data.weekday() == 0:
        close_data = datetime.date.today() - datetime.timedelta(days=2)
    get_stock_data()

