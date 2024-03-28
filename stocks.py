from flask import jsonify, redirect, url_for, render_template, request, Blueprint
from tinkoff.invest import Client, CandleInterval, RequestError, InstrumentIdType
from tinkoff.invest.utils import now
from configparser import ConfigParser
from datetime import timedelta, datetime
import os

stock_bp = Blueprint('stock', __name__, template_folder='templates')
TOKEN = 't.o56s5flLZS8rZ_ooAqIcoFnxjoDMTSQEx1cg1XYWxQAZQ_xulTTwa8Tays7n7nql340YHEY-fgapEYaHift_Tw'

# Чтение FIGI акций из файла конфигурации
config = ConfigParser()
config.read('config.ini')
stocks_config = {}

for key, value in config['stocks'].items():
    figi, name = value.split(',', 1)  # Разделяем строку на FIGI и название акции
    stocks_config[key.upper()] = {'figi': figi, 'name': name}


def format_price(price):
    """Форматирует цену для корректного отображения."""
    if price < 1:
        return round(price, 6)
    else:
        return round(price, 4)

@stock_bp.route('/')
def stock():
    now = datetime.now()
    today_start = now.replace(hour=9, minute=50, second=0, microsecond=0)
    today_end = now

    # Если текущее время до 9:50, используем данные за предыдущий рабочий день
    if now < today_start:
        today_start = (today_start - timedelta(days=1)).replace(hour=9, minute=50)
        today_end = (today_end - timedelta(days=1)).replace(hour=23, minute=59)

    with Client(TOKEN) as client:
        stocks_info = []
        for ticker, info in stocks_config.items():
            try:
                last_price = client.market_data.get_last_prices(figi=[info['figi']]).last_prices[0].price
                currentPrice = last_price.units + last_price.nano / 1e9

                # Получаем данные о цене открытия и текущей цене используя 1-минутные свечи
                candles = client.market_data.get_candles(
                    figi=info['figi'],
                    from_=today_start,
                    to=today_end,
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN
                )

                if candles.candles:
                    openPrice = candles.candles[0].open.units + candles.candles[0].open.nano * 1e-9
                    closePrice = candles.candles[-1].close.units + candles.candles[-1].close.nano * 1e-9
                else:
                    openPrice = currentPrice
                    closePrice = currentPrice

                dayChange = closePrice - openPrice
                dayChangePercent = (dayChange / openPrice * 100) if openPrice else 0

                stocks_info.append({
                    'name': info['name'],
                    'ticker': ticker,
                    'price': format_price(closePrice),  # Используем closePrice как текущую цену
                    'figi': info['figi'],
                    'dayChangePercent': dayChangePercent
                })
            except Exception as e:
                print(f"Ошибка получения данных для {ticker.upper()}: {e}")

        # Сортируем акции по росту и падению
        top_growth_stocks = sorted(stocks_info, key=lambda x: x['dayChangePercent'], reverse=True)[:5]
        top_decline_stocks = sorted(stocks_info, key=lambda x: x['dayChangePercent'])[:5]

        return render_template('index.html', stocks_info=stocks_info, top_growth_stocks=top_growth_stocks,
                               top_decline_stocks=top_decline_stocks)


@stock_bp.route('/<ticker>')
def stock_graph(ticker):
    stock_figi = None
    stock_name = "Название акции не найдено"

    stock_info = stocks_config.get(ticker.upper())  # Использование .upper() для обеспечения сопоставимости ключей
    if stock_info:
        stock_name = stock_info['name']
        stock_figi = stock_info['figi']

    if stock_figi:  # Проверка, что figi был найден
        return render_template('graph.html', ticker=ticker, figi=stock_figi, stock_name=stock_name)
    else:

        return render_template('error.html', message="Акция не найдена")


@stock_bp.route('/<figi>/<interval>')
def get_candles(figi, interval):
    interval_map = {
        '15min': CandleInterval.CANDLE_INTERVAL_5_MIN,
        '1h': CandleInterval.CANDLE_INTERVAL_15_MIN,
        '4h': CandleInterval.CANDLE_INTERVAL_HOUR,
        '1d': CandleInterval.CANDLE_INTERVAL_4_HOUR,
        '1m': CandleInterval.CANDLE_INTERVAL_DAY,
        'all': CandleInterval.CANDLE_INTERVAL_MONTH
    }
    days_map = {
        '15min': 1,
        '1h': 1,
        '4h': 7,
        '1d': 30,
        '1m': 365,
        'all': 365 * 5
    }
    if interval not in interval_map:
        return jsonify({'error': 'Invalid interval'}), 400
    client_interval = interval_map[interval]
    days_to_subtract = days_map[interval]
    from_ = now() - timedelta(days=days_to_subtract)
    to = now()
    with Client(TOKEN) as client:
        candles = client.market_data.get_candles(figi=figi, from_=from_, to=to, interval=client_interval)
        # Модификация здесь
        data = [{
            'Date': str(candle.time.isoformat()),
            'Open': candle.open.units + candle.open.nano * 1e-9,
            'High': candle.high.units + candle.high.nano * 1e-9,
            'Low': candle.low.units + candle.low.nano * 1e-9,
            'Close': candle.close.units + candle.close.nano * 1e-9
        } for candle in candles.candles]
        return jsonify(data)



@stock_bp.route('/stats/<figi>')
def get_today_stats(figi):
    now = datetime.now()
    today_start = now.replace(hour=9, minute=50, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=0, microsecond=0)

    # Если текущее время до 10:00, используем дату предыдущего дня
    if now < today_start:
        today_start = (today_start - timedelta(days=1)).replace(hour=9, minute=50)
        today_end = (today_end - timedelta(days=1)).replace(hour=23, minute=59)

    with Client(TOKEN) as client:
        last_price = client.market_data.get_last_prices(figi=[figi]).last_prices[0].price
        currentPrice = last_price.units + last_price.nano / 1e9

        candles = client.market_data.get_candles(
            figi=figi,
            from_=today_start,
            to=today_end,
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN
        )

        prices = [candle.close.units + candle.close.nano * 1e-9 for candle in candles.candles] if candles.candles else [currentPrice]
        openPrice = candles.candles[0].open.units + candles.candles[0].open.nano * 1e-9 if candles.candles else currentPrice
        closePrice = candles.candles[-1].close.units + candles.candles[-1].close.nano * 1e-9 if candles.candles else currentPrice
        minPrice = min(prices) if prices else currentPrice
        maxPrice = max(prices) if prices else currentPrice

        opening_price_today = prices[0] if prices else currentPrice
        dayChange = currentPrice - opening_price_today
        dayChangePercent = (dayChange / opening_price_today * 100) if opening_price_today else 0

        return jsonify({
            'currentPrice': format_price(currentPrice),
            'dayChange': format_price(dayChange),
            'dayChangePercent': dayChangePercent,
            'openPrice': format_price(openPrice),
            'closePrice': format_price(closePrice),
            'minPrice': format_price(minPrice),
            'maxPrice': format_price(maxPrice)
        })


def get_current_price(ticker):
    stock_info = stocks_config.get(ticker.upper())
    figi=stock_info['figi']
    with Client(TOKEN) as client:
        try:
            last_price = client.market_data.get_last_prices(figi=[figi]).last_prices[0].price
            currentPrice = last_price.units + last_price.nano / 1e9
            return format_price(currentPrice)
        except RequestError as e:
            print(f"Ошибка при получении цены: {e}")
            # Возвращаем None или логичное значение по умолчанию
            return None

def get_name_stock(ticker):
    stock_info = stocks_config.get(ticker.upper())
    return stock_info['name']


@stock_bp.route('/<ticker>/lot')
def get_stock_lot_api(ticker):
    try:
        with Client(TOKEN) as client:
            instruments = client.instruments.shares().instruments  # Получаем список акций
            for instrument in instruments:
                if instrument.ticker == ticker:  # Если тикер совпадает с искомым
                    lot = instrument.lot
                    lot_str = f'акций' if lot != 1 else f'акция'
                    return jsonify({'lot': lot, 'suffix': lot_str}), 200
            return jsonify({'error': 'Lot information not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

