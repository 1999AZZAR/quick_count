import os
import sqlite3
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class JSONHandler(FileSystemEventHandler):
    def __init__(self, source_folder, destination_folder, log_db_path):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.log_db_path = log_db_path

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        time.sleep(5)
        create_or_update_db(event.src_path, self.destination_folder, self.log_db_path)

    def on_deleted(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        time.sleep(5)
        delete_db(event.src_path, self.destination_folder)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".json"):
            return
        time.sleep(5)
        check_and_delete_empty_dbs(self.destination_folder)

def create_or_update_db(json_file, destination_folder, log_db_path):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

            desa, tps = extract_desa_tps(data)
            if desa is not None and tps is not None:
                db_destination = os.path.join(destination_folder, f"{desa}".upper() + ".db")
                conn = sqlite3.connect(db_destination)
                cursor = conn.cursor()
                table_name = f"TPS_{tps}"

                initialize_table(cursor, table_name)
                insert_data(cursor, data, table_name)

                conn.commit()
                conn.close()

                update_log_db(log_db_path, f"{desa}.db")

            else:
                print(f"Error: 'desa' or 'tps' not found in {json_file}")

    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON in {json_file}: {e}")
    except Exception as ex:
        print(f"Error processing {json_file}: {ex}")

def extract_desa_tps(data):
    if len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
        desa = data[0][0].get("desa", None)
        tps = data[0][0].get("tps", None)
        return desa, tps
    return None, None

def initialize_table(cursor, table_name):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (PARTAI TEXT, PARTAI_VAL INTEGER, CALEG TEXT, CALEG_VAL INTEGER)")

def insert_data(cursor, data, table_name):
    partai_labels = data[1][0]["partaiLabels"]
    partai_values = data[1][0]["partaiValues"]
    for partai, value in zip(partai_labels, partai_values):
        cursor.execute(f"INSERT INTO {table_name} (PARTAI, PARTAI_VAL) VALUES (?, ?)", (partai, value))

    caleg_names = data[2][0]["calegNames"]
    caleg_values = data[2][0]["calegValues"]
    for caleg, value in zip(caleg_names, caleg_values):
        cursor.execute(f"INSERT INTO {table_name} (CALEG, CALEG_VAL) VALUES (?, ?)", (caleg, value))

def delete_db(json_file, destination_folder):
    filename = os.path.basename(json_file)
    parts = filename.split('_')
    if len(parts) == 2 and parts[1].endswith(".json"):
        desa = parts[0]
        tps = parts[1][:-5]
        db_destination = os.path.join(destination_folder, f"{desa}.db")
        conn = sqlite3.connect(db_destination)
        cursor = conn.cursor()
        table_name = f"TPS_{tps}"
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()

def check_and_delete_empty_dbs(destination_folder):
    for filename in os.listdir(destination_folder):
        if filename.endswith(".db"):
            db_path = os.path.join(destination_folder, filename)
            if is_db_empty(db_path):
                os.remove(db_path)

def is_db_empty(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return not tables

def update_log_db(log_db_path, db_name):
    conn = sqlite3.connect(log_db_path)
    cursor = conn.cursor()

    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    size = os.path.getsize(os.path.join(destination_folder, db_name))

    cursor.execute("CREATE TABLE IF NOT EXISTS log (name TEXT PRIMARY KEY, date TEXT, size INTEGER)")
    cursor.execute("INSERT OR REPLACE INTO log (name, date, size) VALUES (?, ?, ?)", (db_name, current_date, size))

    conn.commit()
    conn.close()

def process_existing_dbs(destination_folder, log_db_path):
    for filename in os.listdir(destination_folder):
        if filename.endswith(".db"):
            db_path = os.path.join(destination_folder, filename)
            if is_db_empty(db_path):
                os.remove(db_path)
            else:
                update_log_db(log_db_path, filename)

def process_existing_files(source_folder, destination_folder, log_db_path):
    for filename in os.listdir(source_folder):
        if filename.endswith(".json"):
            json_file_path = os.path.join(source_folder, filename)
            create_or_update_db(json_file_path, destination_folder, log_db_path)

if __name__ == "__main__":
    source_folder = '../databased/FROM_DRIVE/json'
    destination_folder = '../databased/PROCEED/db'
    log_db_path = '../databased/PROCEED/log.db'

    process_existing_files(source_folder, destination_folder, log_db_path)
    process_existing_dbs(destination_folder, log_db_path)

    event_handler = JSONHandler(source_folder, destination_folder, log_db_path)
    observer = Observer()
    observer.schedule(event_handler, path=source_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
            check_and_delete_empty_dbs(destination_folder)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
