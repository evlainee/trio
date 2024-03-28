import json
import os

import pytest
from app_factory import create_app
from models import db, User, InvestorPortfolio, Stock
from stocks import format_price, get_name_stock


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_Investing.db',
        'DOWNLOAD_FOLDER': os.path.join(os.path.expanduser('~'), 'Downloads')
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client):
    # Функция для входа пользователя
    return client.post('/auth/login', data={'num': '123456789', 'password': 'test'}, follow_redirects=True)

def test_portfolio_page_without_login(app, client):
    response = client.get('/')
    assert response.status_code == 302  # Проверяем, что пользователь перенаправлен на страницу входа

def test_portfolio_page_with_login(app, client):
    with app.app_context():
        # Создаем тестового пользователя
        test_user = User(name='Test', surname='User', patronymic='Test', num='123456789', password='test')
        db.session.add(test_user)
        db.session.commit()

    with client:
        login(client)
        response = client.get('/portfolio')
        assert b'Please log in to view this page.' not in response.data  # Проверяем, что страница загрузилась без ошибок

def test_replenish_balance(app, client):
    with app.app_context():
        # Создаем тестового пользователя
        test_user = User(name='Test', surname='User', patronymic='Test', num='123456789', password='test')
        db.session.add(test_user)
        db.session.commit()

    with client:
        login(client)
        response = client.post('/portfolio/replenish_balance', data={'amount': 100}, follow_redirects=True)
        assert response.status_code == 200  # Проверяем, что запрос успешно обработан

def test_withdraw_balance(app, client):
    with app.app_context():
        # Создаем тестового пользователя
        test_user = User(name='Test', surname='User', patronymic='Test', num='123456789', password='test')
        test_portfolio = InvestorPortfolio(id=1, free_funds=200)
        db.session.add_all([test_user, test_portfolio])
        db.session.commit()

    with client:
        login(client)
        response = client.post('/portfolio/withdraw_balance', data={'amount': 100}, follow_redirects=True)
        assert response.status_code == 200  # Проверяем, что запрос успешно обработан

def test_trade_action(app, client):
    with app.app_context():
        # Создаем тестового пользователя
        test_user = User(name='Test', surname='User', patronymic='Test', num='123456789', password='test')
        test_portfolio = InvestorPortfolio(id=1, free_funds=5000)
        db.session.add_all([test_user, test_portfolio])
        db.session.commit()

    with client:
        login(client)
        data = {'ticker': 'SBERP', 'quantity': 10, 'price': 300, 'operationType': 'Покупка'}
        response = client.post('/portfolio/trade_action', json=data, follow_redirects=True)
        assert response.status_code == 200  # Проверяем, что запрос успешно обработан

def test_export_excel(app, client):
    with app.app_context():
        # Создаем тестового пользователя
        test_user = User(name='Test', surname='User', patronymic='Test', num='123456789', password='test')
        test_portfolio = InvestorPortfolio(id=1, free_funds=1000)
        test_stock = Stock(name='Sberbank', tiker='SBER', quantity=10, purchase_price=300, portfolio_id=1)
        db.session.add_all([test_user, test_portfolio, test_stock])
        db.session.commit()

    with client:
        login(client)
        response = client.get('/portfolio/export_excel', follow_redirects=True)
        assert response.status_code == 200  # Проверяем, что запрос успешно обработан

@pytest.mark.parametrize("price, expected", [
    (0.00123211, 0.001232),  # Минимальное значение
    (1.2345013, 1.2345),  # Значение больше 1
    (1234.567811, 1234.5678)  # Большое значение
])
def test_format_price(price, expected):
    assert format_price(price) == expected

def test_get_name_stock():
    ticker = "GAZP"  # Пример тикера
    name = get_name_stock(ticker)
    assert name == "Gazprom"  # Предположим, что это название акции


@pytest.mark.parametrize("ticker, expected_lot", [
    ("GAZP", 10),  # Пример тикера и ожидаемой лотности
])
def test_get_stock_lot_api(ticker, expected_lot, client):
    with client:
        login(client)
        response = client.get(f'/stock/{ticker}/lot')
        assert response.status_code == 200  # Проверяем, что запрос успешно обработан
        data = json.loads(response.data)
        assert data['lot'] == expected_lot  # Проверяем полученное значение лотности
