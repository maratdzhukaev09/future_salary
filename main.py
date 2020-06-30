import requests, os
from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_salary(salary_from, salary_to):
    if salary_from == 0 and salary_to == 0:
        return None
    elif salary_from in (None, 0):
        return int(salary_to * 0.8)
    elif salary_to in (None, 0):
        return int(salary_from * 1.2)
    else:
        return int((salary_from + salary_to) / 2)

def predict_rub_salary_hh(vacancy):
    salary_info = vacancy["salary"]
    if salary_info["currency"] == "RUR":
        return predict_salary(salary_info["from"], salary_info["to"])
    else:
        return None

def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] == "rub":
        return predict_salary(vacancy["payment_from"], vacancy["payment_to"])
    else:
        return None

def get_average_salary(vacancies, service):
    salaries_amount = 0
    vacancies_processed = 0
    counter = 0
    for vacancy in vacancies:
        counter += 1
        try:
            if service == "hh":
                salaries_amount += predict_rub_salary_hh(vacancy)
            elif service == "sj":
                salaries_amount += predict_rub_salary_sj(vacancy)
            vacancies_processed += 1
        except TypeError:
            salaries_amount = salaries_amount
    average_salary = int(salaries_amount / vacancies_processed)

    return average_salary, vacancies_processed

def get_language_vacancies_hh(language):
    vacancies = []
    for page_number in range(0, 20):
        params = {
            "text": f"Программист {language}",
            "area": 113,
            "period": 30,
            "page": page_number,
            "per_page": 100
        }
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()

        vacancies += response.json()["items"]
    return vacancies, response.json()["found"]


def get_language_vacancies_info_hh(language):
    vacancies, vacancies_found = get_language_vacancies_hh(language)

    average_salary, vacancies_processed = get_average_salary(vacancies, "hh")

    language_vacancies_info = { 
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }

    return language_vacancies_info

def get_languages_vacancies_info_hh(languages):
    languages_vacancies_info_hh = dict()

    for language in languages:
        languages_vacancies_info_hh[language] = get_language_vacancies_info_hh(language)

    return languages_vacancies_info_hh


def get_language_vacancies_sj(language):
    vacancies = []
    for page_number in range(0, 5):
        params = {
            "catalogues": 48,
            "town": "Москва",
            "page": page_number,
            "count": 100,
            "keyword": language
        }
        headers = {
            "X-Api-App-Id": os.getenv("X-API-APP-ID")
        }
        response = requests.get("https://api.superjob.ru/2.0/vacancies/", params=params, headers=headers)
        response.raise_for_status()

        vacancies += response.json()["objects"]
    return vacancies, response.json()["total"]

def get_language_vacancies_info_sj(language):
    vacancies, vacancies_found = get_language_vacancies_sj(language)

    average_salary, vacancies_processed = get_average_salary(vacancies, "sj")

    language_vacancies_info = { 
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary
    }

    return language_vacancies_info

def get_languages_vacancies_info_sj(languages):
    languages_vacancies_info_sj = dict()

    for language in languages:
        languages_vacancies_info_sj[language] = get_language_vacancies_info_sj(language)

    return languages_vacancies_info_sj

def get_table_data(languages_vacancies_info):
    table_data = [["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]]
    for language, language_info in languages_vacancies_info.items():
        row = [language, language_info["vacancies_found"], language_info["vacancies_processed"], language_info["average_salary"]]
        table_data.append(row)
    return table_data

def main():
    programming_languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go", "Shell", "Objective-C", "Scala", "Swift", "TypeScript"]
    load_dotenv()

    languages_vacancies_info_hh = get_languages_vacancies_info_hh(programming_languages)
    languages_vacancies_info_sj = get_languages_vacancies_info_sj(programming_languages)

    hh_table = AsciiTable(get_table_data(languages_vacancies_info_hh), "HeadHunter Moscow")
    print(hh_table.table)

    sj_table = AsciiTable(get_table_data(languages_vacancies_info_sj), "SuperJob Moscow")
    print(sj_table.table)

if __name__ == "__main__":
    main()