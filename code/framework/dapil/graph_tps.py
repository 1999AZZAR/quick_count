import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import time

time.sleep(15)

data_source = '../databased/PROCEED/db'
data_save = '../interface/static/data/pertps'
graph_info_db = '../interface/static/data/pertps/graph_info.db'

def create_graph_info_table():
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS graph_info
                      (graph_name TEXT NOT NULL UNIQUE,
                       last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def update_graph_info(graph_name):
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO graph_info (graph_name) VALUES (?)''', (graph_name,))
    conn.commit()
    conn.close()

def generate_and_save_graph(db_path, table_name):
    db_name = os.path.splitext(os.path.basename(db_path))[0]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT PARTAI, PARTAI_VAL FROM {table_name}")
    data = cursor.fetchall()
    conn.close()

    data = [('invalid' if row[0] == 'Suara Tidak Sah' else row[0], row[1]) for row in data]
    data = [(row[0].replace('PARTAI ', '') if row[0] else None, row[1]) for row in data]
    partai_names, partai_values = zip(*[(row[0], row[1]) for row in data if row[0] is not None and row[1] is not None])
    partai_values = np.array(partai_values)
    
    fig, ax = plt.subplots(gridspec_kw={'bottom': 0.24})
    bars = ax.bar(partai_names, partai_values, label='PARTAI', color=['red' if name == 'invalid' else 'blue' for name in partai_names])
    ax.set_ylabel('JUMLAH SUARA')
    ax.set_title(f'PEROLEHAN SUARA {table_name} - {db_name}')
    ax.bar(['TOTAL'], [sum(partai_values)], label='TOTAL', color='orange')

    plt.xticks(rotation='vertical')
    ax.legend()

    for bar, value in zip(bars, partai_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                ha='center', va='bottom')

    save_path = os.path.join(data_save, f'{db_name}_{table_name}.png')
    plt.savefig(save_path)
    print(f"generated {db_name}_{table_name}.png")
    plt.close()

    update_graph_info(f'{db_name}_{table_name}')

def get_existing_graphs():
    return {row[0] for row in execute_query('SELECT graph_name FROM graph_info')}

def execute_query(query, parameters=()):
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

def continuously_update_graphs():
    create_graph_info_table()

    while True:
        existing_graphs = get_existing_graphs()

        for db_file in os.listdir(data_source):
            if db_file.endswith(".db"):
                db_path = os.path.join(data_source, db_file)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]
                conn.close()

                for table_name in tables:
                    generate_and_save_graph(db_path, table_name)

        for graph_name in existing_graphs:
            db_name, table_name = graph_name.rsplit('_', 1)
            graph_path = os.path.join(data_save, f'{graph_name}.png')

            if not os.path.isfile(graph_path) or f'{db_name}_{table_name}' not in existing_graphs:
                os.remove(graph_path)
                print(f"deleted {db_name}_{table_name}.png")

        time.sleep(150)

continuously_update_graphs()
