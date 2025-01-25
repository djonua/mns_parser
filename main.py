from fastapi import FastAPI, HTTPException
from parser import MNSParser
from typing import List, Dict, Any, Union

app = FastAPI(
    title="MNS Parser API",
    description="API для получения данных организаций из реестра МНС Абхазии",
    version="1.0.0"
)

def is_inn(query: str) -> bool:
    """Проверяет, является ли запрос ИНН (только цифры)"""
    return query.isdigit()

@app.get("/api/search/{query}")
async def search_organizations(query: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Универсальный поиск организаций.
    Если запрос содержит только цифры - ищет по ИНН.
    В противном случае ищет по наименованию.
    """
    if is_inn(query):
        org = MNSParser.get_organization_by_inn(query)
        if org is None:
            raise HTTPException(status_code=404, detail="Организация не найдена")
        return org.to_json()
    else:
        organizations = MNSParser.get_organizations_by_name(query)
        if not organizations:
            raise HTTPException(status_code=404, detail="Организации не найдены")
        return [org.to_json() for org in organizations]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8987)
