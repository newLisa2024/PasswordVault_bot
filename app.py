from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from tinydb import TinyDB, Query
import random
import string
import os
from dotenv import load_dotenv  # Для загрузки переменных из .env

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)

# Устанавливаем секретный ключ из переменной окружения
app.secret_key = os.getenv('SECRET_KEY')

# Инициализация базы данных (TinyDB)
db = TinyDB('passwords.json')
user_db = TinyDB('users.json')

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Модель пользователя
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


# Загрузка пользователя по id
@login_manager.user_loader
def load_user(user_id):
    user_table = Query()
    user_data = user_db.search(user_table.id == user_id)
    if user_data:
        return User(user_id, user_data[0]['username'], user_data[0]['password_hash'])
    return None


# Главная страница с генерацией и сохранением паролей (доступна только авторизованным пользователям)
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'generate' in request.form:
            password = generate_password()
            return render_template('index.html', password=password)
        elif 'save' in request.form:
            password = request.form['password']
            site = request.form['site']
            account = request.form['account']
            user_id = current_user.id  # Получаем ID текущего пользователя
            db.insert({'user_id': user_id, 'site': site, 'account': account, 'password': password})
            return render_template('index.html', password=None, message="Пароль сохранен!")
    return render_template('index.html')


# Страница для отображения всех сохраненных паролей пользователя
@app.route('/passwords')
@login_required
def view_passwords():
    Password = Query()
    passwords = db.search(Password.user_id == current_user.id)  # Показываем только пароли текущего пользователя
    return render_template('passwords.html', passwords=passwords)


# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем, существует ли уже пользователь
        user_table = Query()
        if user_db.search(user_table.username == username):
            flash("Пользователь с таким именем уже существует!")
            return redirect(url_for('register'))

        # Хешируем пароль с помощью generate_password_hash
        password_hash = generate_password_hash(password)

        # Сохраняем пользователя в базу данных
        user_id = str(len(user_db.all()) + 1)  # Простой ID
        user_db.insert({'id': user_id, 'username': username, 'password_hash': password_hash})

        flash("Регистрация прошла успешно!")
        return redirect(url_for('login'))

    return render_template('register.html')


# Маршрут для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ищем пользователя в базе данных
        user_table = Query()
        user_data = user_db.search(user_table.username == username)

        if user_data:
            user = User(user_data[0]['id'], username, user_data[0]['password_hash'])
            # Проверяем правильность пароля
            if user.verify_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Неверный пароль!")
        else:
            flash("Пользователь не найден!")

    return render_template('login.html')


# Маршрут для выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из системы.")
    return redirect(url_for('login'))


# Функция для генерации случайного пароля
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


if __name__ == '__main__':
    app.run(debug=True)




