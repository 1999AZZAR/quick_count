import sqlite3
import json
import time

# time.sleep(63)

while True:

    # Function to calculate seats based on Sainte-Laguë method
    def calculate_seats(votes, num_seats):
        total_seats = {}
        divisors = [1] * len(votes)  # Initialize divisors for each party
        
        for i in range(num_seats):
            seats = []
            
            for party_number in range(len(votes)):
                quotient = votes[party_number] / divisors[party_number]
                seats.append((party_number + 1, quotient))
            
            seats.sort(key=lambda x: x[1], reverse=True)

            winner = seats[0][0]
            total_seats.setdefault(winner, []).append((i + 1, seats[0][1]))  # Record the total seats for the winner

            divisors[winner - 1] += 2  # Increase the divisor for the winner by 2 for the next round

        return total_seats

    # Connect to SQLite database
    conn = sqlite3.connect('../databased/PROCEED/total_suara.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute a query to fetch data from the 'total_suara' table
    cursor.execute("SELECT partai, jumlah_suara FROM suara_data")

    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Extract party names and values from rows
    partai_names = [row[0] for row in rows]
    partai_values = [row[1] for row in rows]

    # Calculate seats using the Sainte-Laguë method for the first 4 seats only
    num_seats = min(len(partai_values), 4)
    total_seats = calculate_seats(partai_values, num_seats)

    # Prepare the result dictionary
    result_dict = {}
    for party, seats in total_seats.items():
        party_name = partai_names[party - 1]
        total = len(seats)
        seat_numbers = [seat[0] for seat in seats]
        values = [seat[1] for seat in seats]
        result_dict[party_name] = {"total_seats": total, "seat_numbers": seat_numbers, "values": values}

    # Print the result
    for party_name, party_data in result_dict.items():
        print(f"Partai {party_name} mendapatkan sebanyak {party_data['total_seats']} kursi di kursi {party_data['seat_numbers']} dengan nilai {party_data['values']}")

    # Save the result as JSON
    with open('../framework/kursi/result.json', 'w') as json_file:
        json.dump(result_dict, json_file, indent=2)

    # Sleep for 70 seconds before the next iteration
    time.sleep(70)
