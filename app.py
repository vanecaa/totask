from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask import flash
from datetime import datetime, timezone
from collections import defaultdict




app = Flask(__name__)
app.secret_key = 'ksnlsdngg-sfsdgn-esgskejngsng-sskfns!-slnsfnsfsnfnksnfelskfn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///individualtaskmanager.db' 
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#Модель для регистрации пользователя
class User(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(200), unique=True, nullable=False)
  password = db.Column(db.String(200), nullable=False) 


# Модель для задач
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
    is_tracked = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    

# Создаем базу данных
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))   
    tasks = Task.query.filter_by(completed=False).order_by(Task.date).all()  # Сортировка задач по дате
    grouped_tasks = defaultdict(list)
    for task in tasks:
        # Проверяем, что task.date не равен None
        if task.date:
            grouped_tasks[task.date].append(task)
        else:
            # Если date равен None, используем текущую дату
            grouped_tasks[datetime.now(timezone.utc).date()].append(task)
    return render_template('index.html', grouped_tasks=grouped_tasks)
@app.route('/register', methods=['GET', 'POST'])

def register():
     if request.method == 'POST':
         username = request.form.get('username')
         password = request.form.get('password')
         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
         new_user = User(username=username, password=hashed_password)
         db.session.add(new_user)
         db.session.commit()
         return redirect(url_for('login'))
     return render_template('register.html')
 
from flask import flash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
    return render_template('login.html')

    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

def is_authenticated():
    return 'user_id' in session


#Тестовый код для добавления выполненных задач в пункт "completed"
@app.route('/completed_tasks')
def completed_tasks():
    if not is_authenticated():
        return redirect(url_for('login'))
    tasks = Task.query.filter_by(completed=True).all()
    return render_template('completed_tasks.html', tasks=tasks)


#Тестовый код для отслеживания задачи, при нажатии нужной кнопки
@app.route('/toggle_tracking/<int:task_id>', methods=['POST'])
def toggle_tracking(task_id):
    tasks = Task.query.get(task_id)
    if tasks:
        tasks.is_tracked = not tasks.is_tracked
        db.session.commit()
    return redirect(url_for('index'))



# Добавление задачи
@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')  # Получаем дату из формы
    date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now(timezone.utc).date()  # Исправлено
    new_task = Task(title=title, description=description, date=date)  # Создаем задачу с датой
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

# Удаление задачи
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# Отметка задачи как выполненной
@app.route('/complete/<int:id>')
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)