import os
import sqlite3
import matplotlib.pyplot as plt
import time

time.sleep(40)

total_suara_db = '../databased/PROCEED/total_suara.db'
data_source = '../databased/PROCEED/db'
data_save = '../interface/static/data/perdesa'
graph_info_db = '../interface/static/data/perdesa/graph_info.db'

# Create a table to store graph information
def create_graph_info_table():
    try:
        conn = sqlite3.connect(graph_info_db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS graph_info
                          (graph_name TEXT NOT NULL UNIQUE,
                           last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating graph_info table: {e}")
    finally:
        conn.close()

# Create the total_suara.db if it doesn't exist
def create_total_suara_db():
    try:
        conn = sqlite3.connect(total_suara_db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS suara_data
                          (partai TEXT NOT NULL,
                           jumlah_suara INTEGER DEFAULT 0,
                           PRIMARY KEY (partai))''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating total_suara.db: {e}")
    finally:
        conn.close()

# Update graph information in the database
def update_graph_info(graph_name):
    try:
        conn = sqlite3.connect(graph_info_db)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO graph_info (graph_name) VALUES (?)''', (graph_name,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating graph info: {e}")
    finally:
        conn.close()

# Function to get the list of existing graphs
def get_existing_graphs():
    try:
        return {row[0] for row in execute_query('SELECT graph_name FROM graph_info')}
    except sqlite3.Error as e:
        print(f"Error getting existing graphs: {e}")
        return set()

# Function to execute a database query with error handling
def execute_query(query, parameters=()):
    try:
        conn = sqlite3.connect(graph_info_db)
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        conn.commit()
        return result
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        conn.close()

# Function to update total_suara.db with the latest values
def update_total_suara_db(partai, jumlah_suara):
    if partai not in ['TOTAL', 'invalid']:
        try:
            conn = sqlite3.connect(total_suara_db)
            cursor = conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO suara_data (partai, jumlah_suara) VALUES (?, ?)''', (partai, jumlah_suara))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating total_suara.db: {e}")
        finally:
            conn.close()

# Function to combine and save the graph for the entire database
def generate_and_save_combined_graph():
    # Initialize data dictionary to store combined data
    combined_data = {}

    for db_file in os.listdir(data_source):
        if db_file.endswith(".db"):
            db_path = os.path.join(data_source, db_file)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get the list of tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            # Iterate through tables and combine data
            for table_name in tables:
                cursor.execute(f"SELECT PARTAI, PARTAI_VAL FROM {table_name}")
                data = cursor.fetchall()

                for row in data:
                    key = row[0].replace('PARTAI ', '') if row[0] else None

                    # Replace 'Suara Tidak Sah' with 'invalid'
                    key = 'invalid' if key == 'Suara Tidak Sah' else key

                    if key is not None:
                        if key not in combined_data:
                            combined_data[key] = 0

                        # Ignore rows with null values
                        if row[1] is not None:
                            combined_data[key] += row[1]

            conn.close()

    # Exclude 'None' key from combined_data
    combined_data = {k: v for k, v in combined_data.items() if k is not None}

    # Print the final combined data
    print("Combined Data:", combined_data)

    # Update total_suara.db with the latest values
    for partai, jumlah_suara in combined_data.items():
        update_total_suara_db(partai, jumlah_suara)

    # Filter out None values from combined_data
    valid_data = {k: v for k, v in combined_data.items() if k is not None}

    # Check if there is any valid data to plot
    if not valid_data:
        print("No valid data to plot. Skipping.")
        return

    # Plot and save the combined graph
    fig, ax = plt.subplots(gridspec_kw={'bottom': 0.24})

    bars = ax.bar(valid_data.keys(), valid_data.values(), label='PARTAI',
                  color=['red' if name == 'invalid' else 'blue' for name in valid_data.keys()])
    ax.set_ylabel('JUMLAH SUARA')
    ax.set_title('PEROLEHAN SUARA TOTAL')
    ax.bar(['TOTAL'], [sum(valid_data.values())], label='TOTAL', color='orange')

    plt.xticks(rotation='vertical')
    ax.legend()

    # Adjust rotation for better visibility of vote numbers
    for bar, value in zip(bars, valid_data.values()):
        rotation_angle = 45 if value < 100 else 90
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(value),
                ha='center', va='bottom', rotation=rotation_angle)

    save_path = os.path.join(data_save, 'total_dapil.png')
    plt.savefig(save_path)
    print("Generated total_dapil.png")
    plt.close()

    # Update graph information in the database
    update_graph_info('total_dapil')

# Function to continuously update graphs
def continuously_update_graphs():
    create_graph_info_table()
    create_total_suara_db()

    try:
        while True:
            generate_and_save_combined_graph()

            # Remove graphs that are no longer needed
            existing_graphs = get_existing_graphs()
            for graph_name in existing_graphs:
                if not os.path.isfile(os.path.join(data_save, f'{graph_name}.png')):
                    os.remove(os.path.join(data_save, f'{graph_name}.png'))
                    print(f"Deleted {graph_name}.png")

            time.sleep(150)

    except KeyboardInterrupt:
        print("Script interrupted. Exiting gracefully.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Start continuously updating graphs
continuously_update_graphs()
