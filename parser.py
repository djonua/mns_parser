import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Union
import json

@dataclass
class BaseEntity:
    name: str
    inn: str
    registration_date: str
    certificate_number: str
    ogrn: str
    taxpayer_status: str
    status: str

    def to_json(self):
        return {
            'name': self.name,
            'inn': self.inn,
            'registration_date': self.registration_date,
            'certificate_number': self.certificate_number,
            'ogrn': self.ogrn,
            'taxpayer_status': self.taxpayer_status,
            'status': self.status,
            'type': self.entity_type
        }

@dataclass
class Organization(BaseEntity):
    entity_type: str = "organization"

@dataclass
class Entrepreneur(BaseEntity):
    entity_type: str = "entrepreneur"

class MNSParser:
    BASE_URL = "https://mns-ra.org/reestr"
    
    @staticmethod
    def _parse_table_rows(table, entity_class) -> List[Union[Organization, Entrepreneur]]:
        """Парсинг строк таблицы в список организаций или ИП"""
        entities = []
        rows = table.find_all('tr')
        
        # Пропускаем заголовок таблицы
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 7:
                entity = entity_class(
                    name=cells[0].text.strip(),
                    inn=cells[1].text.strip(),
                    registration_date=cells[2].text.strip(),
                    certificate_number=cells[3].text.strip(),
                    ogrn=cells[4].text.strip(),
                    taxpayer_status=cells[5].text.strip(),
                    status=cells[6].text.strip().replace('\xa0', ' ').replace('<br>', '')
                )
                entities.append(entity)
        
        return entities

    @staticmethod
    def get_organization_by_inn(inn: str) -> Optional[Organization]:
        """Получение данных организации по ИНН"""
        try:
            response = requests.post(
                f"{MNSParser.BASE_URL}/search.php",
                data={
                    'search_info': 'None',
                    'search_inn': inn,
                    'search': 'Искать'
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'results'})
            if not table:
                return None

            organizations = MNSParser._parse_table_rows(table, Organization)
            return organizations[0] if organizations else None
            
        except requests.RequestException:
            return None

    @staticmethod
    def get_organizations_by_name(name: str) -> List[Organization]:
        """Получение списка организаций по наименованию"""
        try:
            response = requests.post(
                f"{MNSParser.BASE_URL}/search.php",
                data={
                    'search_info': 'None',
                    'search_name': name,
                    'search': 'Искать'
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'results'})
            if not table:
                return []

            return MNSParser._parse_table_rows(table, Organization)
            
        except requests.RequestException:
            return []

    @staticmethod
    def get_entrepreneur_by_inn(inn: str) -> Optional[Entrepreneur]:
        """Получение данных ИП по ИНН"""
        try:
            print("\n=== Поиск ИП по ИНН ===")
            print(f"ИНН: {inn}")
            
            # Создаем сессию для сохранения cookies
            session = requests.Session()
            
            # Сначала делаем GET запрос на страницу поиска ИП для получения формы
            print("\n-> GET запрос на страницу поиска ИП:")
            print(f"URL: {MNSParser.BASE_URL}/entrepreneur.php")
            
            response = session.get(
                f"{MNSParser.BASE_URL}/entrepreneur.php",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            print(f"Статус ответа: {response.status_code}")
            if response.status_code != 200:
                print("Ошибка при получении страницы поиска")
                return None

            # Формируем данные для поиска как в форме
            data = {
                'search_info': 'None',  # скрытое поле из формы
                'search_inn_1': inn,    # правильное имя поля для ИНН
                'search': 'Искать'      # кнопка поиска
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{MNSParser.BASE_URL}/entrepreneur.php",
                'Origin': MNSParser.BASE_URL
            }

            # Отправляем POST запрос для поиска
            print("\n-> POST запрос для поиска:")
            print(f"URL: {MNSParser.BASE_URL}/search.php")
            print("Данные запроса:", json.dumps(data, indent=2))
            print("Заголовки запроса:", json.dumps(headers, indent=2))
            
            response = session.post(
                f"{MNSParser.BASE_URL}/search.php",
                data=data,
                headers=headers
            )
            
            print(f"Статус ответа: {response.status_code}")
            print("Заголовки ответа:", json.dumps(dict(response.headers), indent=2))
            
            if response.status_code != 200:
                print("Ошибка при выполнении поиска")
                return None

            # Выводим ответ для отладки
            print("\n-> Содержимое ответа:")
            print(response.text[:1000])  # Выводим первую 1000 символов для краткости

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'results'})
            if not table:
                print("Таблица с результатами не найдена")
                return None

            entrepreneurs = MNSParser._parse_table_rows(table, Entrepreneur)
            if not entrepreneurs:
                print("Результаты не найдены")
                return None

            print(f"\nНайдено результатов: {len(entrepreneurs)}")
            return entrepreneurs[0]
            
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    @staticmethod
    def get_entrepreneurs_by_name(lastname: str, firstname: str = None, patronymic: str = None) -> List[Entrepreneur]:
        """Получение списка ИП по ФИО"""
        try:
            print("\n=== Поиск ИП по ФИО ===")
            print(f"Фамилия: {lastname}")
            print(f"Имя: {firstname}")
            print(f"Отчество: {patronymic}")
            
            # Создаем сессию для сохранения cookies
            session = requests.Session()
            
            # Сначала делаем GET запрос на страницу поиска ИП для получения формы
            print("\n-> GET запрос на страницу поиска ИП:")
            print(f"URL: {MNSParser.BASE_URL}/entrepreneur.php")
            
            response = session.get(
                f"{MNSParser.BASE_URL}/entrepreneur.php",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            print(f"Статус ответа: {response.status_code}")
            if response.status_code != 200:
                print("Ошибка при получении страницы поиска")
                return []
            
            # Формируем данные для поиска как в форме
            data = {
                'search_info': 'None',   # скрытое поле из формы
                'surname': lastname,      # правильное имя поля для фамилии
                'name': firstname if firstname else '',    # правильное имя поля для имени
                'patronymic': patronymic if patronymic else '', # правильное имя поля для отчества
                'search': 'Искать'       # кнопка поиска
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{MNSParser.BASE_URL}/entrepreneur.php",
                'Origin': MNSParser.BASE_URL
            }

            # Отправляем POST запрос для поиска
            print("\n-> POST запрос для поиска:")
            print(f"URL: {MNSParser.BASE_URL}/search.php")
            print("Данные запроса:", json.dumps(data, indent=2))
            print("Заголовки запроса:", json.dumps(headers, indent=2))
            
            response = session.post(
                f"{MNSParser.BASE_URL}/search.php",
                data=data,
                headers=headers
            )
            
            print(f"Статус ответа: {response.status_code}")
            print("Заголовки ответа:", json.dumps(dict(response.headers), indent=2))
            
            if response.status_code != 200:
                print("Ошибка при выполнении поиска")
                return []

            # Выводим ответ для отладки
            print("\n-> Содержимое ответа:")
            print(response.text[:1000])  # Выводим первую 1000 символов для краткости

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'results'})
            if not table:
                print("Таблица с результатами не найдена")
                return []

            entrepreneurs = MNSParser._parse_table_rows(table, Entrepreneur)
            if not entrepreneurs:
                print("Результаты не найдены")
                return []

            print(f"\nНайдено результатов: {len(entrepreneurs)}")
            return entrepreneurs
            
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return []

    @staticmethod
    def universal_search(query: str) -> List[Union[Organization, Entrepreneur]]:
        """Универсальный поиск по ИНН или наименованию/ФИО"""
        # Если запрос содержит только цифры, ищем по ИНН
        if query.isdigit():
            # Сначала ищем среди организаций
            org = MNSParser.get_organization_by_inn(query)
            if org:
                return [org]
            # Если не нашли, ищем среди ИП
            entr = MNSParser.get_entrepreneur_by_inn(query)
            if entr:
                return [entr]
            return []
        
        # Если в запросе есть пробелы, разбиваем на части для поиска по ФИО
        if ' ' in query:
            parts = query.split()
            if len(parts) >= 1:
                lastname = parts[0]
                firstname = parts[1] if len(parts) > 1 else None
                patronymic = parts[2] if len(parts) > 2 else None
                # Ищем среди ИП
                entrepreneurs = MNSParser.get_entrepreneurs_by_name(lastname, firstname, patronymic)
                if entrepreneurs:
                    return entrepreneurs
        
        # В остальных случаях ищем по наименованию организации
        return MNSParser.get_organizations_by_name(query) 