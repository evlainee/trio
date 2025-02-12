import os
from tinkoff.invest import Client
from configparser import ConfigParser

TOKEN = 't.o56s5flLZS8rZ_ooAqIcoFnxjoDMTSQEx1cg1XYWxQAZQ_xulTTwa8Tays7n7nql340YHEY-fgapEYaHift_Tw'

def fetch_russian_figi_and_write_to_config(token, config_path="config.ini"):
    # Инициализация API клиента
    with Client(token) as client:
        # Получение списка всех инструментов (акций)
        instruments = client.instruments.shares().instruments

    # Создаем объект ConfigParser
    config = ConfigParser()

    # Добавляем секцию stocks
    config['stocks'] = {}

    # Проходим по списку акций, фильтруя по стране риска (только RU)
    for instrument in instruments:
        if instrument.country_of_risk == "RU":  # Фильтр по стране риска
            ticker = instrument.ticker.upper()
            figi = instrument.figi
            name = instrument.name

            # Добавляем данные в конфиг
            config['stocks'][ticker] = f"{figi},{name}"

    # Сохраняем в файл
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)

    print(f"Данные российских акций успешно сохранены в {config_path}")

# Запуск функции
config_file_path = os.path.join(os.path.dirname(__file__), "config.ini")
fetch_russian_figi_and_write_to_config(TOKEN, config_path=config_file_path)
