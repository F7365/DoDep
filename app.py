from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wjk432wzsxu483f8nss3akdda4od4pu8edd56l37hffd0gf93fvc738dmymdffhlgvd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
cards = []
stats = {}

class User(db.Model):  # База Данных
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    deps = db.Column(db.Integer, default=0, nullable=False)

with app.app_context():  # Создание и инициализация
    db.create_all()

def dodepss(usernames, d):  # Распределение очков
    with app.app_context():
        users = User.query.filter(User.username.in_(usernames)).all()
        for user in users:
            user.deps += d
        db.session.commit()

@app.route('/')
def home():  # Домашняя страница
    if 'username' in session:
        ddps = User.query.filter_by(username=session['username']).first().deps
        return render_template('home.html', username=session['username'], cards=list(reversed(cards)), stats=stats, ddps=ddps)
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def reg():  # Регистрация
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password']
        password2 = request.form['confirm_password']
        if password1 != password2:
            flash('Пароли не совпадают!','error')
            return redirect(url_for('register'))
        if User.query.filter((User.username == username)).first():
            flash('Пользователь с таким именем уже существует!','error')
            return redirect(url_for('register'))
        db.session.add(User(username=username, password=str(hashlib.md5(str(password1).encode()).hexdigest())))
        session['username'] = username
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('reg.html')

@app.route('/login', methods=['GET', 'POST'])
def login():  # Авторизация
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == hashlib.md5(str(password1).encode()).hexdigest():
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль!','error')
    return render_template('login.html')

@app.route('/logout')
def logout():  # Выход с аккаунта
    session.pop('username', None)
    flash('Вы вышли из системы.','info')
    return redirect(url_for('home'))

@app.route('/add_card', methods=['POST'])
def add_card():  # Пост-запрос для создания карточки
    global cards
    carddata = request.get_json()
    cards.append(carddata)
    remove_time = datetime.datetime.now() + datetime.timedelta(hours=carddata['period'])
    stats[carddata['r']] = {'yes': [],
                             'no': []}
    carddata['remove_at'] = remove_time.timestamp()
    return jsonify({'status': 'success'})

@app.route('/remove_card/<idd>', methods=['POST'])
def remove_card(idd):  # Пост-запрос для удаления карточки
    global cards
    index = None
    for card in cards:
        if card['r'] == idd:
            index = card
            break
    if index is not None:
        cards.remove(index)
    return jsonify({'status': 'success'})

@app.route('/razdacha/<idd>/<action>', methods=['POST'])
def razdacha(idd,action):  # Пост-запрос для удаления карточки и раздачи очков
    if action == 'yes':
        dodepss(stats[idd]['yes'],1)
        dodepss(stats[idd]['no'],-1)
    elif action == 'no':
        dodepss(stats[idd]['no'],1)
        dodepss(stats[idd]['yes'],-1)
    index = None
    for card in cards:
        if card['r'] == idd:
            index = card
            break
    if index is not None:
        cards.remove(index)
    del stats[idd]
    return jsonify({'status': 'success'})

@app.route('/card_action/<card_id>', methods=['POST'])
def card_action(card_id):   # Пост-запрос для отслеживания действий пользователя по карточке
    action = request.json.get('action')
    user = session.get('username')
    if action == 'yes':
        stats[card_id]['yes'].append(user)
        if user in stats[card_id]['no']:
            stats[card_id]['no'].remove(user)
    elif action == 'no':
        stats[card_id]['no'].append(user)
        if user in stats[card_id]['yes']:
            stats[card_id]['yes'].remove(user)
    else:
        if user in stats[card_id]['yes']:
            stats[card_id]['yes'].remove(user)
        if user in stats[card_id]['no']:
            stats[card_id]['no'].remove(user)
    return jsonify({'status': 'success'})

@app.errorhandler(404)   # Обработчик несуществующих страниц (ошибок)
def no_page(e):
    flash('Страница не найдена', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    ff=[1,2,3,3]
    app.run()