Запуск командой ```docker compose up```

Функции конструкторы ORM-запросы лежат в функциях в соответсвующих репозиториях (например, в ```src/repositories/menu```)

Реализация кэша:
сделан репозиторий на CRUD дествия для Redis, записи хранятся с помощью RedisJSON. Вместе оба репозитория работают в сущности Unit Of Work```src/uof/uofs```. На все get-запросы отвечает только кеш (при этом они хранятся и в кеше, и в SQL базе данных), а при ```patch```, ```post```, ```delete```, запись обновляется/создаётся/удаляется сначала в SQL базе данных, а затем Redis. Также инвалидируются всё счётчики для родительских сущностей.
