## Docker контейнер
### Порядок установки
1. Установите Docker
2. Получите образ контейнера с помощью команды:
```shell script
docker pull qwertyadrian/tg_autoposter
```
3. Запустите docker контейнер командой (должно завершиться с ошибкой)
```shell script
docker run -it --name <имя_контейнера> tg_autoposter
```
4. Скопируйте файл конфигурации config.ini в созданный контейнер командой:
```shell script
docker cp <путь_до_файла_конфигурации> <имя_контейнера>:/TG_AutoPoster/config.ini
```
5. Если необходимо, скопируйте файл со стоп-словами в созданный контейнер командой:
```shell script
docker cp <путь_до_файла_со_стоп_словами> <имя_контейнера>:/TG_AutoPoster/<имя_файла_со_стоп_словами>
```
6. Повторно запустите контейнер командой (параметр `-ai` необходим только для интерактивного режима, для запуска в фоне можно опустить):
```shell script
docker start -ai <имя_контейнера>
```