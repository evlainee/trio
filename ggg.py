from tinkoff.invest import Client

# Ваш API токен
TOKEN = 't.o56s5flLZS8rZ_ooAqIcoFnxjoDMTSQEx1cg1XYWxQAZQ_xulTTwa8Tays7n7nql340YHEY-fgapEYaHift_Tw'

# FIGI для различных инструментов
figi_dict = {
    'MOEX': 'BBG000BDTBL9',   # Индекс ММВБ
    'USD_RUB': 'RUB000UTSTOM',  # Доллар США (на московской бирже)
    'EUR_RUB': 'EUR_RUB_TOM',   # Евро
    'CNY_RUB': 'CNYRUB_TOM',    # Китайский юань
    'NASDAQ': 'BBG000BLNN42',   # Индекс NASDAQ
    'GOLD': 'SPB000000002',     # Золото
    'BTC_USD': 'BITCOIN/USD',   # Биткойн
}

with Client(TOKEN) as client:
    instruments = client.instruments.shares().instruments
    for instrument in instruments:
        print(f"Ticker: {instrument.ticker}, FIGI: {instrument.figi}")
