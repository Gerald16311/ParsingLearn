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
import requests, json, time
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar

search_name = input(f'Введите искомую должность-')
search_url = f'https://samara.hh.ru/search/vacancy?fromSearchLine=true&text={search_name}'

result_data = {}
head_url = 'https://samara.hh.ru/'

urls_list = []

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.46'}

result = []
# response = requests.get(search_url, headers=headers)
# dom = BeautifulSoup(response.text, 'html.parser')

list_range = int(input(f'Введите количество обрабатываемых страниц - '))

bar = IncrementalBar('Сбор вакансий', max=list_range)
for i in range(0, list_range):
    response = requests.get(f'{search_url}&page=1', headers=headers)
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
y = 1
for url in urls_list:
    response = requests.get(url, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find('div', {'class': 'vacancy-title'})
    vacancy_cost = vacancies.find('span').getText().replace('\xa0', '').split(" ")
    if vacancy_cost[0] == "з/п":
        result_data.update({str(url): {'head_url': head_url,
                                       'Название вакансии': ''.join(vacancies.find('h1').getText()),
                                       'Ссылка на вакансию': url,
                                       'Зарплата до': None,
                                       'Зарплата от': None,
                                       'Зарплата в': None}})
                                       # 'Зарплата': vacancies.find('span').getText().replace('\xa0', '')}})
    elif vacancy_cost[2] == "руб.":
        result_data.update({str(url): {'head_url': head_url,
                                       'Название вакансии': ''.join(vacancies.find('h1').getText()),
                                       'Ссылка на вакансию': url,
                                       'Зарплата до': int(vacancy_cost[1]),
                                       'Зарплата от': None,
                                       'Зарплата в': vacancy_cost[2]}})
                                       # 'Зарплата': vacancy_cost[1],
                                       # 'Зарплата в ': vacancy_cost[2]}})
    else:
        result_data.update({str(url): {'head_url': head_url,
                                       'Название вакансии': ''.join(vacancies.find('h1').getText()),
                                       'Ссылка на вакансию': url,
                                       'Зарплата до': int(vacancy_cost[1]),
                                       'Зарплата от': int(vacancy_cost[3]),
                                       'Зарплата в': vacancy_cost[4]}})
    bar2.next()
    result.append(result_data)

bar.finish()

with open(f'parsed_data_{search_name}.json', 'w', encoding='utf-8') as outfile:
    json.dump(result, outfile, ensure_ascii=False)