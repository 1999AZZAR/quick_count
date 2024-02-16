import sqlite3

def create_user_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

def user_exists(cursor, username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone() is not None

def add_user(cursor, username, password):
    if user_exists(cursor, username):
        print(f"Username '{username}' already exists.")
        choice = input("Do you want to modify the existing user? (yes/no): ").lower()

        if choice == 'yes':
            new_password = input("Enter the new password: ")
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
            print(f"User '{username}' modified successfully.")
        elif choice == 'no':
            print("User addition canceled.")
        else:
            print("Invalid choice. User addition canceled.")
    else:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        print(f"User '{username}' added successfully.")

def list_users(cursor):
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    print("List of Users:")
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Password: {user[2]}")

def remove_user(cursor, username):
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))

def main():
    db_name = 'user_account'
    db = sqlite3.connect('../databased/global'f'{db_name}.db')
    cursor = db.cursor()

    create_user_table(cursor)

    print("Options:")
    print("1. List Users")
    print("2. Add User")
    print("3. Remove User")

    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == '1':
        list_users(cursor)
    elif choice == '2':
        username = input("Enter the username: ")

        if user_exists(cursor, username):
            print(f"Username '{username}' already exists.")
            choice = input("Do you want to modify the existing user? (yes/no): ").lower()

            if choice == 'yes':
                new_password = input("Enter the new password: ")
                cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
                print(f"User '{username}' modified successfully.")
            elif choice == 'no':
                print("User addition canceled.")
            else:
                print("Invalid choice. User addition canceled.")
        else:
            password = input("Enter the password: ")
            add_user(cursor, username, password)
    elif choice == '3':
        username = input("Enter the username to remove: ")
        remove_user(cursor, username)
        print(f"User '{username}' removed successfully.")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

    db.commit()
    db.close()

if __name__ == '__main__':
    main()
