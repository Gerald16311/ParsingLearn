# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем
# должность) с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц
# сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
    # Наименование вакансии.
    # Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к
    # цифрам).
    # Ссылку на саму вакансию.
    # Сайт, откуда собрана вакансия.
#
# По желанию можно добавить ещё параметры вакансии (
# например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов. Общий
# результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
search_name = input(f'Введите искомую должность-')
search_url = f'https://samara.hh.ru/search/vacancy?area=78&fromSearchLine=true&text={search_name}'

result_data = {}
head_url = 'https://samara.hh.ru/'

urls_list = []

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46'}


response = requests.get(search_url, headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')
quotes = dom.find_all('a', {'data-qa': 'vacancy-serp__vacancy-title'})
# pprint(quotes)
print(len(quotes))
if len(quotes) == 0:
    print(f'Вакансий с должностью {search_name} не найдено! Повторите поиск')
else:
    for item in quotes:
        urls_list.append(item.get('href').split('?')[0])
    for url in urls_list:
        response = requests.get(url, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        quotes = dom.find('div', {'class': 'vacancy-title'})
        vacancy_cost = quotes.find('span').getText().replace('\xa0', '').split(" ")

        if vacancy_cost[0] == "з/п":
            result_data.update({str(url): {'head_url': head_url,
                                           'vacancy_title': ''.join(quotes.find('h1').getText()),
                                           'vacancy_url': url,
                                           'vacancy_cost': quotes.find('span').getText().replace('\xa0', '')}})
        elif vacancy_cost[2] == "руб.":
            result_data.update({str(url): {'head_url': head_url,
                                           'vacancy_title': ''.join(quotes.find('h1').getText()),
                                           'vacancy_url': url,
                                           'vacancy_cost': vacancy_cost[1],
                                           'vacancy_cost_value': vacancy_cost[2]}})
        else:
            result_data.update({str(url): {'head_url': head_url,
                                           'vacancy_title': ''.join(quotes.find('h1').getText()),
                                           'vacancy_url': url,
                                           'vacancy_cost_hight': vacancy_cost[1],
                                           'vacancy_cost_low': vacancy_cost[3],
                                           'vacancy_cost_value': vacancy_cost[4]}})

    # pprint(result_data)

    with open(f'parsed_data_{search_name}.json', 'w') as outfile:
        json.dump(result_data, outfile, ensure_ascii=False)

