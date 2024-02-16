import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import time

time.sleep(37)

data_source = '../databased/PROCEED/db'
data_save = '../interface/static/data/percaleg'
graph_info_db = '../interface/static/data/percaleg/graph_info.db'
total_suara_db = '../databased/PROCEED/total_suara.db'

# Create a table to store graph information
def create_graph_info_table():
    with sqlite3.connect(graph_info_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS graph_info
                          (graph_name TEXT NOT NULL UNIQUE,
                           last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Update graph information in the database
def update_graph_info(graph_name):
    with sqlite3.connect(graph_info_db) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO graph_info (graph_name) VALUES (?)''', (graph_name,))

# Function to get the original caleg name before modification
def get_original_name(modified_name):
    # Add more mappings as needed based on your data
    name_mappings = {
        'RATNA': 'RATNA SARI',
        'SAIFUL': 'H. ACHMAD SAIFUL, S.H',
        'MASBAKHAN': 'MASBAKHAH, S.Pd.I',
        # Add more mappings as needed
    }

    return name_mappings.get(modified_name, modified_name)

# Function to combine and save the graph for the entire database
def generate_and_save_combined_graph():
    # Initialize data dictionary to store combined data
    combined_data = {}

    for db_file in os.listdir(data_source):
        if db_file.endswith(".db"):
            db_path = os.path.join(data_source, db_file)
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Get the list of tables in the database
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]

                # Iterate through tables and combine data
                for table_name in tables:
                    cursor.execute(f"SELECT CALEG, CALEG_VAL FROM {table_name}")
                    data = cursor.fetchall()

                    for row in data:
                        key = row[0].replace('CALEG ', '') if row[0] else None

                        # Replace 'Suara Tidak Sah' with 'invalid'
                        key = 'RATNA' if key == 'RATNA SARI' else key
                        key = 'SAIFUL' if key == 'H. ACHMAD SAIFUL, S.H' else key
                        key = 'MASBAKHAN' if key == 'MASBAKHAH, S.Pd.I' else key

                        if key not in combined_data:
                            combined_data[key] = 0
                        combined_data[key] += row[1] if row[1] else 0

    # Filter out None values from combined_data
    valid_data = {k: v for k, v in combined_data.items() if k is not None and k.lower() != 'invalid'}

    # Check if there is any valid data to plot
    if not valid_data:
        print("No valid data to plot. Skipping.")
        return

    # Calculate the total votes for PDI party
    with sqlite3.connect(total_suara_db) as conn_pdi:
        cursor_pdi = conn_pdi.cursor()
        cursor_pdi.execute("SELECT partai, jumlah_suara FROM suara_data WHERE partai = 'PDI'")
        result = cursor_pdi.fetchone()
        pdi_votes = result[1] if result else 0

    # Add a new category for PDI party in the combined data
    valid_data['PARTAI (PDI)'] = pdi_votes - sum(valid_data.values())

    # Plot and save the combined pie charts for each candidate
    for key, value in valid_data.items():
        # Check if key is not None (skip invalid data)
        if key is not None:
            # Retrieve the original caleg name before modification
            original_name = get_original_name(key)

            # Create a pie chart for each candidate
            fig, ax = plt.subplots()
            labels = ['PARTAI (PDI)', f'CALEG {original_name}']
            sizes = [pdi_votes - value, value]
            colors = ['orange', 'gray']

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

            # Save the pie chart with the name of the original caleg
            save_path = os.path.join(data_save, f'{original_name}.png')
            plt.savefig(save_path)
            print(f"Generated {original_name}.png")
            plt.close()

    # Plot and save the combined bar chart showing caleg contribution to total vote
    fig, ax = plt.subplots(gridspec_kw={'bottom': 0.24})
    total_votes = sum(valid_data.values())

    bars = ax.bar(valid_data.keys(), valid_data.values(), label='KONTRIBUSI CALEG', color='blue')
    ax.set_ylabel('JUMLAH SUARA')
    ax.set_title('TOTAL KONTRIBUSI SUARA PERCALEG')
    ax.bar(['TOTAL'], [total_votes], label='TOTAL', color='orange')

    plt.xticks(rotation='vertical')
    ax.legend()

    # Adjust rotation for better visibility of vote numbers
    for bar, value in zip(bars, valid_data.values()):
        rotation_angle = 45 if value < 100 else 90
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                ha='center', va='bottom', rotation=rotation_angle)

    save_path = os.path.join(data_save, 'total_caleg.png')
    plt.savefig(save_path)
    print("Generated total_caleg.png")
    plt.close()

    # Update graph information in the database
    update_graph_info('total_caleg')

# Function to continuously update graphs
def continuously_update_graphs():
    create_graph_info_table()

    while True:
        generate_and_save_combined_graph()

        # Remove graphs that are no longer needed
        existing_graphs = get_existing_graphs()
        for graph_name in existing_graphs:
            if not os.path.isfile(os.path.join(data_save, f'{graph_name}.png')):
                os.remove(os.path.join(data_save, f'{graph_name}.png'))
                print(f"Deleted {graph_name}.png")

        time.sleep(150)

# Function to get the list of existing graphs
def get_existing_graphs():
    with sqlite3.connect(graph_info_db) as conn:
        cursor = conn.cursor()
        return {row[0] for row in cursor.execute('SELECT graph_name FROM graph_info')}

# Function to execute a database query
def execute_query(query, parameters=()):
    with sqlite3.connect(graph_info_db) as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()

# Start continuously updating graphs
continuously_update_graphs()
