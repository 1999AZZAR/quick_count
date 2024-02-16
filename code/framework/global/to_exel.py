import os
import sqlite3
import pandas as pd
import time

time.sleep(1800)

def translate_db_to_excel(folder_path, excel_folder, excel_filename):
    excel_path = os.path.join(excel_folder, excel_filename)
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    
    # Dictionary to store the total sum for each unique 'partai_name' and 'caleg_name'
    total_sum_dict = {}

    for filename in os.listdir(folder_path):
        if filename.endswith(".db"):
            db_path = os.path.join(folder_path, filename)

            try:
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    
                    query = f"SELECT * FROM {table_name}"
                    data_from_db = pd.read_sql_query(query, connection)

                    data_from_db.to_excel(writer, sheet_name=f"{filename}_{table_name}", index=False, startrow=3)

                    workbook  = writer.book
                    worksheet = writer.sheets[f"{filename}_{table_name}"]

                    num_rows, num_cols = data_from_db.shape

                    column_settings = [{'header': column} for column in data_from_db.columns]

                    worksheet.add_table(0, 0, num_rows + 4, num_cols - 1, {'columns': column_settings})

                    # Sum values based on 'partai_name' and 'caleg_name'
                    for index, row in data_from_db.iterrows():
                        if 'PARTAI' in data_from_db.columns and 'PARTAI_VAL' in data_from_db.columns:
                            PARTAI = row['PARTAI']
                            PARTAI_VAL = row['PARTAI_VAL']

                            if PARTAI in total_sum_dict:
                                total_sum_dict[PARTAI] += PARTAI_VAL
                            else:
                                total_sum_dict[PARTAI] = PARTAI_VAL

                        if 'CALEG' in data_from_db.columns and 'CALEG_VAL' in data_from_db.columns:
                            CALEG = row['CALEG']
                            CALEG_VAL = row['CALEG_VAL']

                            if CALEG in total_sum_dict:
                                total_sum_dict[CALEG] += CALEG_VAL
                            else:
                                total_sum_dict[CALEG] = CALEG_VAL

                connection.close()
                
            except sqlite3.Error as e:
                print(f"Error accessing database {filename}: {e}")

    # Create a new data frame with the total sum for each 'partai_name' and 'caleg_name'
    total_df = pd.DataFrame(list(total_sum_dict.items()), columns=['name', 'total_val'])
    total_df.to_excel(writer, sheet_name='total', index=False, startrow=3)

    workbook = writer.book
    worksheet = writer.sheets['total']

    num_rows, num_cols = total_df.shape

    column_settings = [{'header': column} for column in total_df.columns]

    worksheet.add_table(0, 0, num_rows + 4, num_cols - 1, {'columns': column_settings})

    writer._save()
    print(f"Data successfully translated, and 'total' sheet with the sums is saved to {excel_path}")

# Specify the folder for saving Excel files
excel_folder = "../databased/PROCEED/exel"

# Schedule the script to run every 1 hour
while True:
    translate_db_to_excel("../databased/PROCEED/db", excel_folder, "hasil.xlsx")
    time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
