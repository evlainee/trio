import os

from flask import Blueprint, session, flash, redirect, url_for, render_template, request, jsonify, send_file, \
    current_app
from stocks import get_name_stock, get_current_price
from models import InvestorPortfolio, db, Stock
from openpyxl import Workbook


pf_bp = Blueprint('portfolio', __name__, template_folder='templates')


@pf_bp.route('/')
def portfolio():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view this page.')
        return redirect(url_for('auth.login'))

    portfolio = InvestorPortfolio.query.filter_by(id=user_id).first()

    # Если портфель отсутствует, создаем его
    if not portfolio:
        portfolio = InvestorPortfolio(
            id=user_id,
        )
        db.session.add(portfolio)
        db.session.commit()

    # Получаем акции из портфеля
    stocks_data = [{
        'id': stock.id,
        'name': get_name_stock(stock.tiker),
        'ticker': stock.tiker,
        'quantity': stock.quantity,
        'purchase_price': stock.purchase_price,
        'now_price': get_current_price(stock.tiker)
    } for stock in portfolio.stocks.all()]
    total_value_of_stocks = sum(stock['now_price'] * stock['quantity'] for stock in stocks_data)
    total_portfolio_value = portfolio.free_funds + total_value_of_stocks
    # Передаем данные портфеля в шаблон
    return render_template('portfolio.html', stocks_data=stocks_data,
                           free_funds=round(portfolio.free_funds, 2), total_value=round(total_portfolio_value, 2))




@pf_bp.route('/replenish_balance', methods=['POST'])
def replenish_balance():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    amount = float(request.form['amount'])  # Преобразование строки в число
    user_portfolio = InvestorPortfolio.query.filter_by(id=user_id).first()
    if user_portfolio:
        user_portfolio.free_funds += amount
        db.session.commit()
        flash('Баланс успешно пополнен на {} руб.'.format(amount))
    else:
        # Создаем новый портфель, если у пользователя его еще нет
        new_portfolio = InvestorPortfolio(id=user_id, free_funds=amount)
        db.session.add(new_portfolio)
        db.session.commit()
        flash('Портфель создан и баланс успешно пополнен на {} руб.'.format(amount))
    return redirect(url_for('portfolio.portfolio'))

@pf_bp.route('/withdraw_balance', methods=['POST'])
def withdraw_balance():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    amount = float(request.form['amount'])  # Преобразование строки в число
    user_portfolio = InvestorPortfolio.query.filter_by(id=user_id).first()
    if user_portfolio and user_portfolio.free_funds >= amount:
        user_portfolio.free_funds -= amount
        db.session.commit()
        flash('Средства на сумму {} руб. успешно выведены.'.format(amount))
    else:
        flash('Недостаточно средств для вывода.')
    return redirect(url_for('portfolio.portfolio'))

@pf_bp.route('/trade_action', methods=['POST'])
def trade_action():
    if 'user_id' not in session:
        return jsonify({'message': 'Пользователь не авторизован'}), 401

    user_id = session['user_id']
    data = request.json
    ticker = data['ticker']
    quantity = int(data['quantity'])
    price = float(data['price'])
    operation_type = data['operationType']

    portfolio = InvestorPortfolio.query.filter_by(id=user_id).one()

    stock = Stock.query.filter_by(portfolio_id=user_id, tiker=ticker).first()

    if operation_type == 'Покупка':
        total_cost = price * quantity
        if portfolio.free_funds >= total_cost:
            if stock:
                # Расчет новой средней стоимости покупки
                old_total_cost = stock.purchase_price * stock.quantity
                new_total_cost = price * quantity
                new_average_price = (old_total_cost + new_total_cost) / (stock.quantity + quantity)

                stock.quantity += quantity
                stock.purchase_price = new_average_price
            else:
                new_stock = Stock(name=get_name_stock(ticker), tiker=ticker, quantity=quantity, purchase_price=price,
                                  portfolio_id=user_id)
                db.session.add(new_stock)
            portfolio.free_funds -= total_cost
        else:
            return jsonify({'message': f'Недостаточно средств для покупки'}), 400

    elif operation_type == 'Продажа':
        if stock and stock.quantity >= quantity:
            stock.quantity -= quantity
            if stock.quantity == 0:
                db.session.delete(stock)
            portfolio.free_funds += price * quantity
        else:
            return jsonify({'message': f'Недостаточно акций для продажи'}), 400

    db.session.commit()
    return jsonify({'message': f'Операция {operation_type} выполнена успешно'})


@pf_bp.route('/export_excel')
def export_excel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    portfolio = InvestorPortfolio.query.filter_by(id=user_id).first()
    if not portfolio:
        return redirect(url_for('portfolio.portfolio'))

    # Create the Excel file
    wb = Workbook()
    ws = wb.active
    ws.title = "Портфель"

    # Add headers
    headers = ['Название', 'Цена', 'Количество', 'Стоимость', 'За все время']
    ws.append(headers)

    # Add data rows
    for stock in portfolio.stocks:
        row = [
            get_name_stock(stock.tiker),
            f"{stock.purchase_price}₽ → {get_current_price(stock.tiker)}₽",
            stock.quantity,
            f"{round(get_current_price(stock.tiker) * stock.quantity, 2)}₽",
            f"{round((get_current_price(stock.tiker) - stock.purchase_price) * stock.quantity, 2)}₽"
        ]
        ws.append(row)

    excel_file_path = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'user_portfolio.xlsx')
    wb.save(excel_file_path)

    return send_file(excel_file_path, as_attachment=True)



