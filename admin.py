from sqlalchemy import cast, String
from flask import request, redirect, render_template, url_for, flash, jsonify, Blueprint
from models import db, User

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/')
def admin_panel():
    return render_template('admin_panel.html')

@admin_bp.route('/search_users', methods=['GET'])
def search_users():
    search_query = request.args.get('query', '')
    search_field = request.args.get('field', '')
    sort_field = request.args.get('sort', 'id')
    sort_direction = request.args.get('direction', 'asc')

    query = User.query

    if search_query:
        if search_field in ['name', 'surname', 'num', 'date_registered']:
            search_expression = f'%{search_query}%'
            if search_field == 'name':
                query = query.filter(User.name.ilike(search_expression))
            elif search_field == 'surname':
                query = query.filter(User.surname.ilike(search_expression))
            elif search_field == 'num':
                query = query.filter(User.num.ilike(search_expression))
            elif search_field == 'date_registered':
                query = query.filter(cast(User.date_registered, String).like(f'%{search_query}%'))

    if sort_field in ['id', 'name', 'surname', 'num', 'date_registered']:
        if sort_direction == 'asc':
            query = query.order_by(getattr(User, sort_field).asc())
        else:
            query = query.order_by(getattr(User, sort_field).desc())

    users = query.all()
    users_data = [{'id': user.id,
                   'name': user.name,
                   'surname': user.surname,
                   'num': user.num,
                   'date_registered': user.date_registered.strftime('%Y-%m-%d %H:%M')}
                  for user in users]

    return jsonify(users_data)



@admin_bp.route('/user/<int:user_id>/update_role', methods=['POST'])
def update_user_role(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.role = data['role']
    db.session.commit()
    return jsonify({'message': 'User role updated successfully'}), 200

@admin_bp.route('/user/<int:user_id>')
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    # Предполагая, что у пользователя может быть портфель, получаем его акции
    stocks = []
    if user.portfolio:
        stocks = user.portfolio.stocks.all()
    return render_template('user_details.html', user=user, stocks=stocks)



@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удален.')
    return redirect(url_for('auth.admin_panel'))