from flask import Flask, redirect, url_for
from models import db, User, InvestorPortfolio


def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '12345678'

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Investing.db'

    db.init_app(app)  # Связываем экземпляр db с приложением Flask

    with app.app_context():
        db.create_all()  # Создаем таблицы в БД, если их нет

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    # Регистрация синейпечатей
    from login_register import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from stocks import stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stock')

    from portfolio import pf_bp
    app.register_blueprint(pf_bp, url_prefix='/portfolio')

    return app
