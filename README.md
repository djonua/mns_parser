# MNS Parser API

API для получения данных организаций из реестра МНС Абхазии.

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/djonua/mns_parser.git
cd mns_parser
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8987`

## API Endpoints

### Универсальный поиск `/api/search/{query}`

- Если запрос содержит только цифры, выполняется поиск по ИНН
- В противном случае выполняется поиск по наименованию

Примеры:
```bash
# Поиск по ИНН
curl http://localhost:8987/api/search/12025352

# Поиск по наименованию
curl http://localhost:8987/api/search/СТЭМЛАБ
```

## Ответ API

```json
{
  "name": "Название организации",
  "inn": "ИНН",
  "registration_date": "Дата регистрации",
  "certificate_number": "Номер сертификата",
  "ogrn": "ОГРН",
  "taxpayer_status": "Статус налогоплательщика",
  "status": "Состояние"
}
``` 