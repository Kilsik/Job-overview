# Сравниваем вакансии программистов

Приложение предназначено для оценки имеющихся вакансий для программистов в разрезе язков программирования.

### Как установить

Python3 должен быть уже установлен.

Рекомендуется использовать [virtualenv/venv](https://docs.python.org/3/library/venv.html) для изоляции проекта.
Затем используйте pip (или pip3 если есть конфликт с Python2) для
установки зависимостей:
```
pip install -r requirements.txt
```

Для работы Вам также понадобится ```Secret key``` API-сервиса [SuperJob](https://api.superjob.ru/). Положите его в переменную окружения SUPERJOB_SECRET_KEY.


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).