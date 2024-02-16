import subprocess
import os
import signal
import logging
import shutil
from flask import Flask, render_template, redirect, url_for, request, g, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import json

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['USER_DATABASE'] = os.environ.get('USER_DATABASE', '../databased/global/user_account.db')
app.config['DESA_DATABASE'] = os.environ.get('DESA_DATABASE', '../databased/global/list_pemilih.db')
app.config['DRIVE_DATABASE'] = os.environ.get('DRIVE_DATABASE', '../databased/FROM_DRIVE/json/json_log.db')
app.config['IMAGE_DATABASE'] = os.environ.get('IMAGE_DATABASE', '../databased/FROM_DRIVE/img/img_log.db')
app.config['PROCEED_DATABASE'] = os.environ.get('PROCEED_DATABASE', '../databased/PROCEED/log.db')
app.config['STATIC_FOLDER'] = 'static'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

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

def connect_image_db():
    return sqlite3.connect(app.config['IMAGE_DATABASE'])

def connect_proceed_db():
    return sqlite3.connect(app.config['PROCEED_DATABASE'])

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

def get_image_db():
    if 'image_db' not in g:
        g.image_db = connect_image_db()
    return g.image_db

def get_proceed_db():
    if 'proceed_db' not in g:
        g.proceed_db = connect_proceed_db()
    return g.proceed_db

@app.teardown_appcontext
def close_dbs(error):
    if hasattr(g, 'user_db'):
        g.user_db.close()
    if hasattr(g, 'desa_db'):
        g.desa_db.close()
    if hasattr(g, 'drive_db'):
        g.drive_db.close()
    if hasattr(g, 'image_db'):
        g.image_db.close()
    if hasattr(g, 'proceed_db'):
        g.proceed_db.close()

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
    partai_names = [row[0] for row in cursor.fetchall()]
    return render_template('built/perpartai.html', partai_names=partai_names)

@app.route('/percaleg')
@login_required
def percaleg():
    desa_db = get_desa_db()
    cursor = desa_db.execute('SELECT nama FROM caleg WHERE nama IS NOT NULL') 
    caleg_name = [row[0] for row in cursor.fetchall()]
    return render_template('built/percaleg.html', caleg_name=caleg_name)

@app.route('/kursi')
@login_required
def kursi():
    result_json_path = '/media/azzar/betha/Downloads/project/quick_count/framework/kursi/result.json'
    with open(result_json_path, 'r') as json_file:
        result_dict = json.load(json_file)
    return render_template('built/kursi.html', result_dict=result_dict)

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
        return render_template('error/404.html')

@app.route('/data')
@login_required
def data():
    return render_template('built/data.html')

@app.route('/rawdrive')
@login_required
def rawdrive():
    drive_db = get_drive_db()
    cursor = drive_db.execute('SELECT name FROM file_log WHERE name IS NOT NULL') 
    drive_data = [row[0] for row in cursor.fetchall()]
    return render_template('built/rawdrive.html', drive_data=drive_data)

@app.route('/image')
@login_required
def image():
    image_db = get_image_db()
    cursor = image_db.execute('SELECT name FROM file_log WHERE name IS NOT NULL') 
    drive_image = [row[0] for row in cursor.fetchall()]
    return render_template('built/image.html', drive_image=drive_image)

@app.route('/proceed')
@login_required
def proceed():
    proceed_db = get_proceed_db()
    cursor = proceed_db.execute('SELECT name FROM log WHERE name IS NOT NULL') 
    proceed_data = [row[0] for row in cursor.fetchall()]
    return render_template('built/proceed.html', proceed_data=proceed_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/download_db')
@login_required
def download_db():
    source_folder = '/media/azzar/betha/Downloads/project/quick_count/databased/PROCEED/db'
    zip_filename = 'db_archive.zip'

    temp_dir = '/tmp/db_temp'
    os.makedirs(temp_dir, exist_ok=True)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            shutil.copy2(file_path, temp_dir)

    shutil.make_archive(os.path.join('/tmp', zip_filename.split('.')[0]), 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    return send_from_directory('/tmp', zip_filename, as_attachment=True)

@app.route('/download_hasil')
@login_required
def download_hasil():
    source_folder = '/media/azzar/betha/Downloads/project/quick_count/databased/PROCEED/exel'
    zip_filename = 'hasil.zip'

    temp_dir = '/tmp/hasil_temp'
    os.makedirs(temp_dir, exist_ok=True)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            shutil.copy2(file_path, temp_dir)

    shutil.make_archive(os.path.join('/tmp', zip_filename.split('.')[0]), 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    return send_from_directory('/tmp', zip_filename, as_attachment=True)

@app.route('/download_json')
@login_required
def download_json():
    source_folder = '/media/azzar/betha/Downloads/project/quick_count/databased/FROM_DRIVE/json'
    zip_filename = 'json_archive.zip'

    temp_dir = '/tmp/json_temp'
    os.makedirs(temp_dir, exist_ok=True)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            shutil.copy2(file_path, temp_dir)

    shutil.make_archive(os.path.join('/tmp', zip_filename.split('.')[0]), 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    return send_from_directory('/tmp', zip_filename, as_attachment=True)

@app.route('/download_image')
@login_required
def download_image():
    source_folder = '/media/azzar/betha/Downloads/project/quick_count/databased/FROM_DRIVE/img'
    zip_filename = 'image_archive.zip'

    temp_dir = '/tmp/image_temp'
    os.makedirs(temp_dir, exist_ok=True)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        if os.path.isfile(file_path):
            shutil.copy2(file_path, temp_dir)

    shutil.make_archive(os.path.join('/tmp', zip_filename.split('.')[0]), 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    return send_from_directory('/tmp', zip_filename, as_attachment=True)

@app.errorhandler(Exception)
def handle_error(error):
    error_code = getattr(error, 'code')
    error_description = getattr(error, 'description')
    return render_template('error/error.html', error_code=error_code, error_description=error_description)

def run_drive_mon():
    drive_mon_script = '/media/azzar/betha/Downloads/project/quick_count/framework/global/drive_mon.py'
    drive_mon_process = subprocess.Popen(['python3', drive_mon_script])
    return drive_mon_process

def run_data_translate():
    data_translate_script = '/media/azzar/betha/Downloads/project/quick_count/framework/global/data_trans.py'
    data_translate_process = subprocess.Popen(['python3', data_translate_script])
    return data_translate_process

def run_graph_tps():
    graph_tps_script = '/media/azzar/betha/Downloads/project/quick_count/framework/dapil/graph_tps.py'
    graph_tps_process = subprocess.Popen(['python3', graph_tps_script])
    return graph_tps_process

def run_graph_desa():
    graph_desa_script = '/media/azzar/betha/Downloads/project/quick_count/framework/dapil/graph_desa.py'
    graph_desa_process = subprocess.Popen(['python3', graph_desa_script])
    return graph_desa_process

def run_graph_dapil():
    graph_dapil_script = '/media/azzar/betha/Downloads/project/quick_count/framework/dapil/graph_dapil.py'
    graph_dapil_process = subprocess.Popen(['python3', graph_dapil_script])
    return graph_dapil_process

def run_graph_caleg():
    graph_caleg_script = '/media/azzar/betha/Downloads/project/quick_count/framework/caleg/graph_caleg.py'
    graph_caleg_process = subprocess.Popen(['python3', graph_caleg_script])
    return graph_caleg_process

def run_graph_kursi():
    graph_kursi_script = '/media/azzar/betha/Downloads/project/quick_count/framework/kursi/kursi.py'
    graph_kursi_process = subprocess.Popen(['python3', graph_kursi_script])
    return graph_kursi_process

def run_pie_chart():
    pie_chart_script = '/media/azzar/betha/Downloads/project/quick_count/framework/dapil/pie_chart.py'
    pie_chart_process = subprocess.Popen(['python3', pie_chart_script])
    return pie_chart_process

def run_exel():
    exel_script = '/media/azzar/betha/Downloads/project/quick_count/framework/global/to_exel.py'
    exel_process = subprocess.Popen(['python3', exel_script])
    return exel_process

if __name__ == '__main__':
    drive_mon_process = run_drive_mon()
    data_translate_process = run_data_translate()
    graph_tps_process = run_graph_tps()
    graph_desa_process = run_graph_desa()
    graph_dapil_process = run_graph_dapil()
    graph_caleg_process = run_graph_dapil()
    graph_kursi_process = run_graph_kursi()
    pie_chart_process = run_pie_chart()
    exel_process = run_exel()

    try:
        app.run(host="0.0.0.0", port=3000, threaded=False)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: Stopping subprocesses...")
        drive_mon_process.terminate()
        data_translate_process.terminate()
        graph_tps_process.terminate()
        graph_desa_process.terminate()
        graph_dapil_process.terminate()
        graph_caleg_process.terminate()
        graph_kursi_process.terminate()
        pie_chart_process.terminate()
        exel_process.terminate()

        drive_mon_process.wait()
        data_translate_process.wait()
        graph_tps_process.wait()
        graph_desa_process.wait()
        graph_dapil_process.wait()
        graph_caleg_process.wait()
        graph_kursi_process.wait()
        pie_chart_process.wait()
        exel_process.wait()

        logging.info("Subprocesses terminated.")
    finally:
        os.kill(os.getpid(), signal.SIGTERM)
