from fastapi import FastAPI, HTTPException, Query
from parser import MNSParser
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

app = FastAPI(
    title="MNS Parser API",
    description="API для получения данных организаций и ИП из реестра МНС Абхазии",
    version="1.0.0"
)

# Модели для POST запросов
class SearchQuery(BaseModel):
    query: str

class OrganizationSearch(BaseModel):
    name: str

class EntrepreneurSearch(BaseModel):
    lastname: str
    firstname: Optional[str] = None
    patronymic: Optional[str] = None

@app.get("/api/search/{query}")
async def universal_search(query: str) -> Dict[str, Any]:
    """
    Универсальный поиск по ИНН или наименованию/ФИО.
    
    - Если запрос содержит только цифры, выполняется поиск по ИНН
    - Если запрос содержит пробелы, выполняется поиск по ФИО для ИП
    - В остальных случаях выполняется поиск по наименованию
    """
    results = MNSParser.universal_search(query)
    return {
        "results": [entity.to_json() for entity in results],
        "total": len(results)
    }

@app.post("/api/search")
async def universal_search_post(query: SearchQuery) -> Dict[str, Any]:
    """Универсальный поиск по ИНН или наименованию/ФИО (POST метод)."""
    results = MNSParser.universal_search(query.query)
    return {
        "results": [entity.to_json() for entity in results],
        "total": len(results)
    }

@app.get("/api/organization/inn/{inn}")
async def get_organization_by_inn(inn: str) -> Dict[str, Any]:
    """
    Получение информации об организации по ИНН
    """
    org = MNSParser.get_organization_by_inn(inn)
    if org is None:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org.to_json()

@app.get("/api/organizations/name")
async def get_organizations_by_name(query: str = Query(..., description="Наименование организации")) -> Dict[str, Any]:
    """Поиск организаций по наименованию"""
    organizations = MNSParser.get_organizations_by_name(query)
    return {
        "results": [org.to_json() for org in organizations],
        "total": len(organizations)
    }

@app.post("/api/organizations/search")
async def search_organizations_post(search: OrganizationSearch) -> Dict[str, Any]:
    """Поиск организаций по наименованию (POST метод)"""
    organizations = MNSParser.get_organizations_by_name(search.name)
    return {
        "results": [org.to_json() for org in organizations],
        "total": len(organizations)
    }

@app.get("/api/entrepreneur/inn/{inn}")
async def get_entrepreneur_by_inn(inn: str) -> Dict[str, Any]:
    """
    Получение информации об ИП по ИНН
    """
    entrepreneur = MNSParser.get_entrepreneur_by_inn(inn)
    if entrepreneur is None:
        raise HTTPException(status_code=404, detail="ИП не найден")
    return entrepreneur.to_json()

@app.get("/api/entrepreneurs/name")
async def get_entrepreneurs_by_name(
    lastname: str = Query(..., description="Фамилия"),
    firstname: str = Query(None, description="Имя"),
    patronymic: str = Query(None, description="Отчество")
) -> Dict[str, Any]:
    """Поиск ИП по ФИО"""
    entrepreneurs = MNSParser.get_entrepreneurs_by_name(lastname, firstname, patronymic)
    return {
        "results": [entr.to_json() for entr in entrepreneurs],
        "total": len(entrepreneurs)
    }

@app.post("/api/entrepreneurs/search")
async def search_entrepreneurs_post(search: EntrepreneurSearch) -> Dict[str, Any]:
    """Поиск ИП по ФИО (POST метод)"""
    entrepreneurs = MNSParser.get_entrepreneurs_by_name(
        search.lastname,
        search.firstname,
        search.patronymic
    )
    return {
        "results": [entr.to_json() for entr in entrepreneurs],
        "total": len(entrepreneurs)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8987)
