import requests
import os

from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)


def get_vacancy_hh(lang):
    url = 'https://api.hh.ru/vacancies'
    all_pages = []
    for page in count(0):
        job_params = {
            "professional_role": '96',
            "area": '1',
            "period": '30',
            "page": page,
            "per_page": '100',
            "text": lang,
        }
        response = requests.get(url, params=job_params)
        response.raise_for_status()
        vacancy_json = response.json()
        all_pages.append(vacancy_json)
        if page == vacancy_json['pages'] - 1:
            break
    return all_pages


def get_vacansy_sj(lang):
    superjob_key = os.environ["SUPERJOB_SECRET_KEY"]
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    superjob_headers = {
        'X-Api-App-Id': superjob_key,
    }
    all_pages = []
    for page in count(0):
        superjob_params = {
            'page': page,
            'count': '100',
            # 'catalogues': 48,
            'town': 4,
            'period': 30,
            'keyword': lang,
            'keywords': ['программист', 'разработчик', 'разработка']
        }
        superjob_response = requests.get(superjob_url,
                                         headers=superjob_headers,
                                         params=superjob_params)
        superjob_response.raise_for_status()
        all_pages.append(superjob_response.json())
        if page == 4:
            break
    return all_pages


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if not salary:
        return None
    if not salary['currency'] == 'RUR':
        return None
    if salary['gross']:
        gross = 0.87
    else:
        gross = 1
    if salary['from']:
        salary_from = int(salary['from'] * gross)
    else:
        salary_from = None
    if salary['to']:
        salary_to = int(salary['to'] * gross)
    else:
        salary_to = None
    return predict_salary(salary_from, salary_to)


def predict_rub_salary_sj(vacancy):
    if not vacancy['currency'] == 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    if salary_from == 0:
        salary_from = None
    if salary_to == 0:
        salary_to = None
    return predict_salary(salary_from, salary_to)


def get_stat_hh(languages):
    language_prices = []
    for lang in languages:
        pages = get_vacancy_hh(lang)
        amount_vacancies = pages[0]['found']
        if amount_vacancies <= 100:
            continue
        sum_salaries = 0
        amount_salaries = 0
        average_salary = 0
        for page in pages:
            vacancies = page['items']
            for vacancy in vacancies:
                salary = predict_rub_salary_hh(vacancy)
                if not salary:
                    continue
                sum_salaries += salary
                amount_salaries += 1
        if not amount_salaries == 0:
            average_salary = sum_salaries // amount_salaries
        language_prices.append([lang, amount_vacancies,
                                amount_salaries, average_salary])
    return language_prices


def get_stat_sj(languages):
    language_prices = []
    for lang in languages:
        pages = get_vacansy_sj(lang)
        amount_vacancies = pages[0]['total']
        sum_salaries = 0
        amount_salaries = 0
        average_salary = 0
        for page in pages:
            page_vacancies = page['objects']
            for vacancy in page_vacancies:
                salary = predict_rub_salary_sj(vacancy)
                if not salary:
                    continue
                sum_salaries += salary
                amount_salaries += 1
        if not amount_salaries == 0:
            average_salary = sum_salaries // amount_salaries
        language_prices.append([lang, amount_vacancies,
                                amount_salaries, average_salary])
    return language_prices


def drow_table(lang_prices, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано',
         'Средняя зарплата']
    ]
    for stat in lang_prices:
        lang = stat[0]
        total_vacancies = stat[1]
        treated_vacancies = stat[2]
        average_salary = stat[3]
        table_data.append([lang, total_vacancies, treated_vacancies,
                           average_salary])
    table_instance = AsciiTable(table_data, title)
    print(table_instance.table)


def main():
    load_dotenv()
    languages = [
        'Python',
        'JavaScript',
        'Java',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        '1С',
        'C',
        'Go',
        'Shell',
        'Objective-C',
        'Scala',
        'Swift',
        'TypeScript',
        'R',
        'PowerShell'
    ]
    language_prices_hh = get_stat_hh(languages)
    title_hh = 'HeadHunter Moscow'
    drow_table(language_prices_hh, title_hh)
    print()
    language_prices_sj = get_stat_sj(languages)
    title_sj = 'SuperJob Moscow'
    drow_table(language_prices_sj, title_sj)


if __name__ == '__main__':
    main()
