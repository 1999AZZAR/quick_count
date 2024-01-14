import subprocess
from flask import Flask, render_template, redirect, url_for, request, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import os

app = Flask(__name__)
app.config['USER_DATABASE'] = '/media/azzar/betha/Downloads/project/quick_count/databased/quick_access.db'
app.config['DESA_DATABASE'] = '/media/azzar/betha/Downloads/project/quick_count/databased/list_pemilih.db'
app.config['DRIVE_DATABASE'] = '/media/azzar/betha/Downloads/project/quick_count/databased/downloaded/file_log.db'
app.config['STATIC_FOLDER'] = 'static'
app.config['SECRET_KEY'] = os.urandom(24)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @staticmethod
    def get(user_id):
        return User(user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def connect_user_db():
    return sqlite3.connect(app.config['USER_DATABASE'])

def connect_desa_db():
    return sqlite3.connect(app.config['DESA_DATABASE'])

def connect_drive_db():
    return sqlite3.connect(app.config['DRIVE_DATABASE'])

def get_user_db():
    if 'user_db' not in g:
        g.user_db = connect_user_db()
    return g.user_db

def get_desa_db():
    if 'desa_db' not in g:
        g.desa_db = connect_desa_db()
    return g.desa_db

def get_drive_db():
    if 'drive_db' not in g:
        g.drive_db = connect_drive_db()
    return g.drive_db

@app.teardown_appcontext
def close_dbs(error):
    if hasattr(g, 'user_db'):
        g.user_db.close()
    if hasattr(g, 'desa_db'):
        g.desa_db.close()
    if hasattr(g, 'drive_db'):
        g.drive_db.close()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user_id = username + password

    user_db = get_user_db()

    cursor = user_db.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    if user:
        login_user(User(user_id=user_id))
        return redirect(url_for('perpartai'))
    else:
        return render_template('login.html', error='Invalid credentials. Please try again.')

@app.route('/perpartai')
@login_required
def perpartai():
    desa_db = get_desa_db()
    cursor = desa_db.execute('SELECT partai FROM partai WHERE partai IS NOT NULL') 
    partai_name = [row[0] for row in cursor.fetchall()]

    return render_template('built/perpartai.html', partai_name=partai_name)

@app.route('/percaleg')
@login_required
def percaleg():
    desa_db = get_desa_db()
    cursor = desa_db.execute('SELECT nama FROM caleg WHERE nama IS NOT NULL') 
    caleg_name = [row[0] for row in cursor.fetchall()]

    return render_template('built/percaleg.html', caleg_name=caleg_name)

@app.route('/perdesa')
@login_required
def perdesa():
    desa_db = get_desa_db()
    cursor = desa_db.execute('SELECT namadesa FROM desa WHERE namadesa IS NOT NULL') 
    desa_names = [row[0] for row in cursor.fetchall()]

    return render_template('built/perdesa.html', desa_names=desa_names)

@app.route('/pertps/<desa_names>')
@login_required
def pertps(desa_names):
    desa_db = get_desa_db()
    cursor = desa_db.execute('SELECT tps FROM desa WHERE namadesa=?', (desa_names,))
    tps_data = cursor.fetchone()

    if tps_data:
        tps_numbers = tps_data[0]
        return render_template('built/pertps.html', desa_tps=tps_numbers.split('\n'), selected_desa=desa_names)
    else:
        return render_template('404.html')

@app.route('/rawdrive')
@login_required
def rawdrive():
    drive_db = get_drive_db()
    cursor = drive_db.execute('SELECT name FROM file_log WHERE name IS NOT NULL') 
    drive_data = [row[0] for row in cursor.fetchall()]

    return render_template('built/rawdrive.html', drive_data=drive_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(Exception)
def handle_error(error):
    error_code = getattr(error, 'code')
    error_description = getattr(error, 'description')
    return render_template('error/error.html', error_code=error_code, error_description=error_description)

def run_drive_mon():
    # Path to drive_mon.py script
    drive_mon_script = '/media/azzar/betha/Downloads/project/quick_count/framework/drive_mon.py'
    
    subprocess.Popen(['python3', drive_mon_script])

if __name__ == '__main__':
    run_drive_mon()
    app.run(host="0.0.0.0", port=3000)