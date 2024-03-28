
from tinkoff.invest import Client, InstrumentIdType

TOKEN = 't.o56s5flLZS8rZ_ooAqIcoFnxjoDMTSQEx1cg1XYWxQAZQ_xulTTwa8Tays7n7nql340YHEY-fgapEYaHift_Tw'


def get_lot_by_ticker(ticker):
    try:
        with Client(TOKEN) as client:
            instruments = client.instruments.shares().instruments  # Получаем список акций
            for instrument in instruments:
                if instrument.ticker == ticker:  # Если тикер совпадает с искомым
                    return f'Лотность для тикера {ticker}: {instrument.lot}'
            return f'Тикер {ticker} не найден'
    except Exception as e:
        return f'Ошибка: {e}'

print(get_lot_by_ticker("VTBR"))  # Пример использования