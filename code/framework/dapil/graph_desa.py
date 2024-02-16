import os
import sqlite3
import matplotlib.pyplot as plt
import time

time.sleep(27)

data_source = '../databased/PROCEED/db'
data_save = '../interface/static/data/perdesa'
graph_info_db = '../interface/static/data/perdesa/graph_info.db'

# Create a table to store graph information
def create_graph_info_table():
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS graph_info
                      (graph_name TEXT NOT NULL UNIQUE,
                       last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Update graph information in the database
def update_graph_info(graph_name):
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO graph_info (graph_name) VALUES (?)''', (graph_name,))
    conn.commit()
    conn.close()

# Function to get the list of existing graphs
def get_existing_graphs():
    return {row[0] for row in execute_query('SELECT graph_name FROM graph_info')}

# Function to execute a database query
def execute_query(query, parameters=()):
    conn = sqlite3.connect(graph_info_db)
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Function to combine and save the graph for a specific desa
def generate_and_save_combined_graph(db_path, desa_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    # Initialize data dictionary to store combined data
    combined_data = {}

    # Iterate through tables and combine data for the specified desa
    for table_name in tables:
        cursor.execute(f"SELECT PARTAI, PARTAI_VAL FROM {table_name}")
        data = cursor.fetchall()

        for row in data:
            key = row[0].replace('PARTAI ', '') if row[0] else None

            # Replace 'Suara Tidak Sah' with 'invalid'
            key = 'invalid' if key == 'Suara Tidak Sah' else key

            if key not in combined_data:
                combined_data[key] = 0
            combined_data[key] += row[1] if row[1] else 0

    conn.close()

    # Filter out None values from combined_data
    valid_data = {k: v for k, v in combined_data.items() if k is not None}

    # Check if there is any valid data to plot
    if not valid_data:
        print(f"No valid data to plot for {desa_name}. Skipping.")
        return

    # Plot and save the combined graph
    fig, ax = plt.subplots(gridspec_kw={'bottom': 0.24})

    bars = ax.bar(valid_data.keys(), valid_data.values(), label='PARTAI',
                  color=['red' if name == 'invalid' else 'blue' for name in valid_data.keys()])
    ax.set_ylabel('JUMLAH SUARA')
    ax.set_title(f'PEROLEHAN SUARA TOTAL {desa_name}')
    ax.bar(['TOTAL'], [sum(valid_data.values())], label='TOTAL', color='orange')

    plt.xticks(rotation='vertical')
    ax.legend()

    for bar, value in zip(bars, valid_data.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                ha='center', va='bottom')

    save_path = os.path.join(data_save, f'{desa_name}.png')
    plt.savefig(save_path)
    print(f"Generated {desa_name}.png")
    plt.close()

    # Update graph information in the database
    update_graph_info(f'{desa_name}')

# Function to continuously update graphs
def continuously_update_graphs():
    create_graph_info_table()

    while True:
        for db_file in os.listdir(data_source):
            if db_file.endswith(".db"):
                db_path = os.path.join(data_source, db_file)
                conn = sqlite3.connect(db_path)

                # Get the desa name from the database file name
                desa_name = os.path.splitext(os.path.basename(db_file))[0]

                generate_and_save_combined_graph(db_path, desa_name)

                conn.close()

        # Remove graphs that are no longer needed
        existing_graphs = get_existing_graphs()
        for graph_name in existing_graphs:
            if not os.path.isfile(os.path.join(data_save, f'{graph_name}.png')):
                os.remove(os.path.join(data_save, f'{graph_name}.png'))
                print(f"Deleted {graph_name}.png")

        time.sleep(150)

# Start continuously updating graphs
continuously_update_graphs()
