# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, которая будет
# добавлять только новые вакансии/продукты в вашу базу. +
#

from pprint import pprint

import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dkf
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar

client = MongoClient('127.0.0.1', 27017)
db = client['HH_vacancies']  # database
vacancies_db = db.vacancies  # collections

search_url = f'https://samara.hh.ru/vacancies/inzhener'
head_url = 'https://samara.hh.ru/'
urls_list = []
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46'}

response = requests.get(f'{search_url}', headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')
max_list_range = dom.find_all('a', {'class': 'bloko-button', 'data-qa': 'pager-page'})
list_range = int(max_list_range[-1].getText())


def vacancies_parse():
    bar = IncrementalBar('Сбор вакансий', max=list_range)
    for i in range(0, list_range):
        response = requests.get(f'{search_url}?page={i}', headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancies = dom.find_all('a', {'data-qa': 'vacancy-serp__vacancy-title'})
        if len(vacancies) == 0:
            print(f'Вакансий с должностью {search_name} не найдено! Повторите поиск')
        else:
            for item in vacancies:
                urls_list.append(item.get('href').split('?')[0])
        bar.next()

    bar.finish()

    bar2 = IncrementalBar('Сбор информаций о вакансий', max=len(urls_list))
    for url in urls_list:
        vacancy_id = str(url).split('/')[-1]
        if vacancies_db.count_documents({'_id': vacancy_id}) > 0:
            pass
            # print('такая вакансия есть в базе')
        else:
            response = requests.get(url, headers=headers)
            if response.status_code < 400:
                dom = BeautifulSoup(response.text, 'html.parser')
                vacancies_name = dom.find('div', {'class': 'vacancy-title'}).find('h1').getText()
                vacancy_cost = dom.find('div', {'class': 'vacancy-title'}).find('span').get_text().replace('\xa0',
                                                                                                           '').split(
                    " ")
                if vacancy_cost[0] == "з/п":
                    vacancies_db.insert_one({'_id': str(vacancy_id),
                                             'head_url': head_url,
                                             'name': vacancies_name,
                                             'url': url,
                                             'salary max': None,
                                             'salary min': None,
                                             'salary currency': None})
                elif vacancy_cost[2] == "руб.":
                    vacancies_db.insert_one({'_id': str(vacancy_id),
                                             'head_url': head_url,
                                             'name': vacancies_name,
                                             'url': url,
                                             'salary max': int(vacancy_cost[1]),
                                             'salary min': None,
                                             'salary currency': vacancy_cost[2]})
                else:
                    vacancies_db.insert_one({'_id': str(vacancy_id),
                                             'head_url': head_url,
                                             'name': vacancies_name,
                                             'url': url,
                                             'salary min': int(vacancy_cost[1]),
                                             'salary max': int(vacancy_cost[3]),
                                             'salary currency': vacancy_cost[4]})
        bar2.next()


# vacancies_parse() # парсинг вакансий, занесение в базу

# 2. Написать функцию, которая производит поиск и выводит на
# экран вакансии с заработной платой больше введённой суммы (необходимо анализировать оба поля зарплаты).
def vacancies_find_in_DB():
    salary_find = int(input('Введите искомую ЗП - '))
    # pprint(list(vacancies_db.find({'salary min': {'$gt': salary_find}})))
    pprint(list(vacancies_db.find({'$or': [
        {'salary min': {'$gt': salary_find}},
        {'salary max': {'$gt': salary_find}}
    ]})))


vacancies_find_in_DB()
