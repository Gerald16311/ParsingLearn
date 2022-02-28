import requests, hashlib
from pprint import pprint
from lxml import html
from pymongo import MongoClient

url = 'https://lenta.ru/'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46'}

response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

news_cards = dom.xpath("//div[contains(@class, 'topnews')]/a[contains(@class, 'card')]")

client = MongoClient('127.0.0.1', 27017)
db = client['News']  # database
news_db = db.news  # collections

news_list = []

for item in news_cards:
    news = {}
    news_name = item.xpath(".//*[contains(@class,'card')]/text()")[0]
    news_link = url + item.xpath(".//@href")[0]
    news_date = '-'.join(item.xpath(".//@href")[0].split('/')[2:5]) + ' ' + item.xpath(".//*[contains(@class,"
                                                                                       "'card')]/text()")[1]

    news['_id'] = hashlib.sha1(news_name.encode()).hexdigest()
    news['name'] = news_name
    news['date'] = news_date
    news['link'] = news_link

    news_list.append(news)
    news_db.insert_one(news)


pprint(news_list)
