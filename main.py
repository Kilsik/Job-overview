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


def get_pages_hh(lang):
    url = 'https://api.hh.ru/vacancies'
    all_pages = []
    id_profession = 96
    id_region = 1
    days = 30
    amount_per_page = 100
    for page in count(0):
        job_params = {
            "professional_role": id_profession,
            "area": id_region,
            "period": days,
            "page": page,
            "per_page": amount_per_page,
            "text": lang,
        }
        response = requests.get(url, params=job_params)
        response.raise_for_status()
        vacancies_page = response.json()
        all_pages.append(vacancies_page)
        if page == vacancies_page['pages'] - 1:
            break
    return all_pages


def get_pages_sj(lang, superjob_key):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    superjob_headers = {
        'X-Api-App-Id': superjob_key,
    }
    all_pages = []
    amount_per_page = 100
    id_town = 4
    days = 30
    max_pages = 5
    for page in count(0):
        superjob_params = {
            'page': page,
            'count': amount_per_page,
            'town': id_town,
            'period': days,
            'keyword': lang,
            'keywords': ['программист', 'разработчик', 'разработка']
        }
        superjob_response = requests.get(superjob_url,
                                         headers=superjob_headers,
                                         params=superjob_params)
        superjob_response.raise_for_status()
        all_pages.append(superjob_response.json())
        if page == max_pages - 1:
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
    if not salary_from:
        salary_from = None
    if not salary_to:
        salary_to = None
    return predict_salary(salary_from, salary_to)


def get_stat_hh(languages):
    statistic = []
    min_amount = 100
    for lang in languages:
        pages = get_pages_hh(lang)
        amount_vacancies = pages[0]['found']
        if amount_vacancies < min_amount:
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
        if amount_salaries:
            average_salary = sum_salaries // amount_salaries
        statistic.append([lang, amount_vacancies,
                                amount_salaries, average_salary])
    return statistic


def get_stat_sj(languages, superjob_key):
    statistic = []
    for lang in languages:
        pages = get_pages_sj(lang, superjob_key)
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
        if amount_salaries:
            average_salary = sum_salaries // amount_salaries
        statistic.append([lang, amount_vacancies,
                                amount_salaries, average_salary])
    return statistic


def drow_table(statistic, title):
    table_lines = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано',
         'Средняя зарплата']
    ]
    for stat in statistic:
        lang = stat[0]
        total_vacancies = stat[1]
        treated_vacancies = stat[2]
        average_salary = stat[3]
        table_lines.append(stat)
    table_instance = AsciiTable(table_lines, title)
    print(table_instance.table)


def main():
    load_dotenv()
    superjob_key = os.environ["SUPERJOB_SECRET_KEY"]
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
    statistic_hh = get_stat_hh(languages)
    title_hh = 'HeadHunter Moscow'
    drow_table(statistic_hh, title_hh)
    print()
    statistic_sj = get_stat_sj(languages, superjob_key)
    title_sj = 'SuperJob Moscow'
    drow_table(statistic_sj, title_sj)


if __name__ == '__main__':
    main()
