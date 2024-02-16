import os
import threading 
import time
import io
import sqlite3
import random
import signal
from datetime import datetime
from googleapiclient.discovery import build
import ssl

script_path = os.path.dirname(os.path.abspath(__file__))
secret_file_path = os.path.join(script_path, '.secret')
with open(secret_file_path, 'r') as secret_file:
    secret_data = secret_file.read()
    exec(secret_data)

# Google Drive API setup
service = build('drive', 'v3', developerKey=API_KEY)

# Variable to indicate whether the script should continue running
running = True

def initialize_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_log (
            name TEXT,
            download_timestamp TEXT,
            file_size INTEGER,
            drive_modified_time TEXT
        )
    ''')
    conn.commit()

    return conn, cursor

def list_files(service, folder_id):
    result = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, size, modifiedTime)").execute()
    files = result.get('files', [])
    return files

def download_file(service, file_id, file_name, download_path, cursor):
    file_path = os.path.join(download_path, file_name)
    request = service.files().get_media(fileId=file_id)
    downloader = io.FileIO(file_path, 'wb')

    retries = 4
    while retries > 0:
        try:
            content = request.execute()
            if content is not None:
                downloader.write(content)
                break
            else:
                print("Received None content. Retrying...")
        except ssl.SSLError as e:
            print(f"SSL Error: {e}. Retrying...")
            time.sleep(3)
            retries -= 1

    if retries == 0:
        print("Failed to download file after multiple attempts.")

    if downloader:
        downloader.close()  # Close the downloader after writing

    file_info = service.files().get(fileId=file_id, fields="size, modifiedTime").execute()
    file_size = file_info.get('size', 0)
    drive_modified_time = file_info.get('modifiedTime', '')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO file_log (name, download_timestamp, file_size, drive_modified_time) VALUES (?, ?, ?, ?)', 
                   (file_name.upper(), timestamp, file_size, drive_modified_time))
    cursor.connection.commit()

def remove_file(file_name, download_path, cursor):
    file_path = os.path.join(download_path, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

    cursor.execute('DELETE FROM file_log WHERE name = ?', (file_name,))
    cursor.connection.commit()

# Function to monitor a specific folder
def monitor_drive(folder_id, download_path, db_path):
    conn, cursor = initialize_database(db_path)

    while running:
        cursor.execute('SELECT name, drive_modified_time FROM file_log')
        downloaded_files = {row[0]: row[1] for row in cursor.fetchall()}

        files = list_files(service, folder_id)

        print(f"Folder: {folder_id}")

        for file in files:
            file_name = file['name']
            drive_modified_time = file['modifiedTime']
            if file_name not in downloaded_files or downloaded_files[file_name] != drive_modified_time:
                print(f"Downloading existing file: {file_name}...")
                download_file(service, file['id'], file_name, download_path, cursor)
                random_delay = random.uniform(5, 10)
                time.sleep(random_delay)

        time.sleep(25)

    # Close database connection when the script stops
    conn.close()

# Signal handler for termination
def signal_handler(signum, frame):
    global running
    print("Received termination signal. Stopping the script.")
    running = False

# Register the signal handler for termination signals
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Create threads for each monitoring task
thread1 = threading.Thread(target=monitor_drive, args=(FOLDER_ID, DOWNLOAD_PATH, os.path.join(DOWNLOAD_PATH, 'json_log.db')))
thread2 = threading.Thread(target=monitor_drive, args=(FOLDER_ID_2, DOWNLOAD_PATH_2, os.path.join(DOWNLOAD_PATH_2, 'img_log.db')))

# Start the threads
print("Monitoring First Folder")
thread1.start()

# Generate a random delay between 10 to 20 seconds
random_delay = random.uniform(10, 20)
time.sleep(random_delay)

# Start the second thread
print("Monitoring Second Folder")
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()
