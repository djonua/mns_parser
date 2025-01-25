import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json

@dataclass
class Organization:
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
            'status': self.status
        }

class MNSParser:
    BASE_URL = "https://mns-ra.org/reestr/search.php"
    
    @staticmethod
    def _parse_table_rows(table) -> List[Organization]:
        """Парсинг строк таблицы в список организаций"""
        organizations = []
        rows = table.find_all('tr')
        
        # Пропускаем заголовок таблицы
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) >= 7:
                org = Organization(
                    name=cells[0].text.strip(),
                    inn=cells[1].text.strip(),
                    registration_date=cells[2].text.strip(),
                    certificate_number=cells[3].text.strip(),
                    ogrn=cells[4].text.strip(),
                    taxpayer_status=cells[5].text.strip(),
                    status=cells[6].text.strip().replace('\xa0', ' ').replace('<br>', '')
                )
                organizations.append(org)
        
        return organizations

    @staticmethod
    def get_organization_by_inn(inn: str) -> Optional[Organization]:
        """Получение данных организации по ИНН"""
        try:
            response = requests.post(
                MNSParser.BASE_URL,
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

            organizations = MNSParser._parse_table_rows(table)
            return organizations[0] if organizations else None
            
        except requests.RequestException:
            return None

    @staticmethod
    def get_organizations_by_name(name: str) -> List[Organization]:
        """Получение списка организаций по наименованию"""
        try:
            response = requests.post(
                MNSParser.BASE_URL,
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

            return MNSParser._parse_table_rows(table)
            
        except requests.RequestException:
            return [] 