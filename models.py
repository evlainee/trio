from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    patronymic = db.Column(db.String(30), nullable=False)
    num = db.Column(db.String(11), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="Investor")
    date_registered = db.Column(db.DateTime, default=datetime.now())

    # Один пользователь имеет один портфель
    portfolio = db.relationship('InvestorPortfolio', backref='user', uselist=False, lazy=True, cascade="all, delete-orphan")

    # Другие связи пользователя
    managed_funds = db.relationship('InvestmentFund', backref='manager', lazy=True, cascade="all, delete-orphan")
    investments = db.relationship('Investment', backref='investor', lazy=True, cascade="all, delete-orphan")
    published_news = db.relationship('MarketNews', backref='publisher', lazy=True, cascade="all, delete-orphan")
    forecasts = db.relationship('Forecast', backref='creator', lazy=True, cascade="all, delete-orphan")
    created_strategies = db.relationship('Strategy', backref='author', lazy=True, cascade="all, delete-orphan")
    subscriptions = db.relationship('Subscription', backref='subscriber', lazy=True, cascade="all, delete-orphan")

class InvestmentFund(db.Model):
    __tablename__ = 'investment_funds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fund_id = db.Column(db.Integer, db.ForeignKey('investment_funds.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class MarketNews(db.Model):
    __tablename__ = 'market_news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    id = db.Column(db.Integer, primary_key=True)
    security = db.Column(db.String(100), nullable=False)
    prediction = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

class Strategy(db.Model):
    __tablename__ = 'strategies'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    funds = db.relationship('InvestmentFund', backref='strategy', lazy=True)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.id'), nullable=False)

class InvestorPortfolio(db.Model):
    __tablename__ = 'investor_portfolios'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    free_funds = db.Column(db.Float, nullable=False, default=1000.0)  # Свободные средства для инвестирования (подарочные 1000)
    stocks = db.relationship('Stock', backref='portfolio', lazy='dynamic')

class Stock(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tiker = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('investor_portfolios.id'), nullable=False)
