from flask import Flask, render_template, request, redirect, url_for, session
import random
import string
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Для сессий

# Инициализация базы данных (можно использовать SQLite, TinyDB или другую)
db = TinyDB('passwords.db')


# Функция для генерации случайного пароля
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


# Главная страница с функционалом генерации и сохранения паролей
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Если пользователь нажал на кнопку "Сгенерировать пароль"
        if 'generate' in request.form:
            password = generate_password()
            return render_template('index.html', password=password)

        # Если пользователь сохраняет пароль
        elif 'save' in request.form:
            password = request.form['password']
            user_id = session.get('user_id', 'anonymous')
            db.insert({'user_id': user_id, 'password': password})
            return render_template('index.html', password=None, message="Пароль сохранен!")

    return render_template('index.html')


# Страница для отображения всех сохраненных паролей
@app.route('/passwords')
def view_passwords():
    user_id = session.get('user_id', 'anonymous')
    Password = Query()
    passwords = db.search(Password.user_id == user_id)
    return render_template('passwords.html', passwords=passwords)


if __name__ == '__main__':
    app.run(debug=True)
