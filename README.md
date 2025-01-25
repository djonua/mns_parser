# MNS API

API для получения данных организаций и индивидуальных предпринимателей из реестра Министерства по налогам и сборам Республики Абхазия.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Запустите сервер:
```bash
python main.py
```

По умолчанию сервер запускается на `http://localhost:8987`

## API Endpoints

### Универсальный поиск

#### GET метод
`GET /api/search/{query}`

Выполняет поиск по ИНН или наименованию/ФИО. Если запрос содержит только цифры, выполняется поиск по ИНН (сначала среди организаций, затем среди ИП). Если в запросе есть пробелы, выполняется поиск по ФИО ИП и наименованию организации.

Примеры:
```
# Поиск по ИНН
GET /api/search/20015387

# Поиск по ФИО ИП
GET /api/search/Джонуа Дамей Борисович

# Поиск по наименованию организации
GET /api/search/РЕСТОРАНЫ АБХАЗИИ
```

#### POST метод (рекомендуемый)
`POST /api/search`

Тело запроса (JSON):
```json
{
    "query": "ООО \"Гаруда-экспресс\""
}
```

### Поиск организаций

#### По ИНН
`GET /api/organization/inn/{inn}`

Пример:
```
GET /api/organization/inn/11007917
```

#### По наименованию

##### GET метод
`GET /api/organizations/name?query={name}`

Пример:
```
GET /api/organizations/name?query=РЕСТОРАНЫ АБХАЗИИ
```

##### POST метод (рекомендуемый)
`POST /api/organizations/search`

Тело запроса (JSON):
```json
{
    "name": "ООО \"Гаруда-экспресс\""
}
```

### Поиск индивидуальных предпринимателей

#### По ИНН
`GET /api/entrepreneur/inn/{inn}`

Пример:
```
GET /api/entrepreneur/inn/20015387
```

#### По ФИО

##### GET метод
`GET /api/entrepreneurs/name?lastname={lastname}&firstname={firstname}&patronymic={patronymic}`

Все параметры кроме `lastname` являются опциональными.

Пример:
```
GET /api/entrepreneurs/name?lastname=Джонуа&firstname=Дамей&patronymic=Борисович
GET /api/entrepreneurs/name?lastname=Джонуа&firstname=Дамей
```

##### POST метод (рекомендуемый)
`POST /api/entrepreneurs/search`

Тело запроса (JSON):
```json
{
    "lastname": "Джонуа",
    "firstname": "Дамей",
    "patronymic": "Борисович"
}
```

## Формат ответа

Успешный ответ возвращается в формате JSON:
```json
{
    "results": [
        {
            "name": "Наименование или ФИО",
            "inn": "ИНН",
            "registration_date": "Дата регистрации",
            "certificate_number": "Серия/Номер бланка",
            "ogrn": "ОГРН",
            "taxpayer_status": "Статус налогоплательщика",
            "status": "Состояние",
            "type": "organization|entrepreneur"
        }
    ],
    "total": 1
}
```

В случае ошибки или если ничего не найдено:
```json
{
    "detail": "Описание ошибки"
}
```

## Примечание по URL-кодированию

При использовании GET методов, специальные символы в параметрах (включая кавычки, пробелы и т.д.) автоматически кодируются. Рекомендуется использовать POST методы для запросов с сложными параметрами, содержащими специальные символы. 

## Сервер для тестов: http://193.124.35.97:8987/api/search
