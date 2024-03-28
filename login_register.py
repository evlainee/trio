from sqlalchemy import cast, String
from flask import request, redirect, render_template, url_for, flash, jsonify, session, Blueprint
from models import db, User, InvestorPortfolio


auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        num = request.form['num']
        password = request.form['password']
        user = User.query.filter_by(num=num).first()
        if user and user.password == password:
            session['user_id'] = user.id  # Сохраняем ID пользователя в сессии
            if user.role == 'Administrator':
                return redirect(url_for('admin.admin_panel'))  # Перенаправление для администратора
            return redirect(url_for('portfolio.portfolio'))  # Перенаправление для обычного пользователя
        else:
            # Если учетные данные неверны, возвращаем сообщение об ошибке
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        patronymic = request.form['patronymic']
        num = request.form['num']
        password = request.form['password']
        if User.query.filter_by(num=num).first():
            flash('Username already exists')
        else:
            new_user = User(name=name, surname=surname, patronymic=patronymic, num=num, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))
    return render_template('register.html')