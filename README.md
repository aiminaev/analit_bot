# Telegram бот аналитик

Реализован следующий функционал:

1. Регистрация пользователя в одну из двух групп, в зависимости от которых он будет иметь доступ к отчетам:

- Аналитик
- Продакт менеджер

2. ID пользователя, его имя и группу бот записывает в БД
3. Бот имеет две команды. Аналитик имеет доступ к обеим командам, продукт имеет доступ только к команде 1
4. При запросе первой команды бот присылает в ЛС отчет по следующей логике:

- Для ключевых столбцов в файле бот должен сравнивать значение в последний день из файла со средним и медианным
  значением столбца за предыдущие 30 дней.

5. При отправке второй команды бот присылает в ЛС отчет по следующей логике:

- Бот проверяет актуальность данных в файле по дате и отправляет сообщение об этом

## Способ запуска

1. Вставить token своего telegram бота в файле bot.py
2. Выполнить следующие команды:

```
docker-compose up -d --build
```

4. Запустить бота в Telegram командой /start
