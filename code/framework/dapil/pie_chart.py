import os
import sqlite3
import matplotlib.pyplot as plt
import time

def generate_and_save_individual_pie_charts():
    try:
        conn = sqlite3.connect(total_suara_db)
        cursor = conn.cursor()

        cursor.execute("SELECT partai, jumlah_suara FROM suara_data")
        data = cursor.fetchall()

        for row in data:
            partai = row[0]
            jumlah_suara = row[1]

            if partai not in ['TOTAL', 'invalid']:
                labels = [partai, 'Others']
                sizes = [jumlah_suara, sum([r[1] for r in data if r[0] not in ['TOTAL', 'invalid', partai]])]

                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['orange', 'gray'])
                ax.axis('equal')

                save_path = os.path.join(data_save, f'{partai.upper()}.png')
                plt.savefig(save_path)
                print(f"Generated {partai.upper()}.png")
                plt.close()

        conn.close()

    except sqlite3.Error as e:
        print(f"Error generating individual pie charts: {e}")
        time.sleep(60)  # Sleep for 60 seconds on error

def continuously_update_individual_pie_charts():
    try:
        while True:
            generate_and_save_individual_pie_charts()

            existing_pie_charts = {f'{partai.upper()}.png' for partai in get_existing_pie_charts()}
            for pie_chart_name in existing_pie_charts:
                if not os.path.isfile(os.path.join(data_save, pie_chart_name)):
                    os.remove(os.path.join(data_save, pie_chart_name))
                    print(f"Deleted {pie_chart_name}")

            time.sleep(150)

    except KeyboardInterrupt:
        print("Script interrupted. Exiting gracefully.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        time.sleep(60)  # Sleep for 60 seconds on error

def get_existing_pie_charts():
    try:
        return [file.split('.')[0] for file in os.listdir(data_save) if file.endswith('.png')]
    except Exception as e:
        print(f"Error getting existing pie charts: {e}")
        return []

# Set your file paths
total_suara_db = '../databased/PROCEED/total_suara.db'
data_save = '../interface/static/data/perpartai'

# Start continuously updating individual pie charts
continuously_update_individual_pie_charts()
