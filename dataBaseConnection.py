import pyodbc
import sys
from JSONcheck import check_json_file
from staticticsGenerate import generate_statistics


def get_connection():
    server = 'den1.mssql7.gear.host'
    database = 'crowd'
    username = 'crowd'
    password = 'Sa9X?-41M3nR'
    driver = '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' +
                          server + ';PORT=1433;DATABASE=' +
                          database + ';UID=' + username +
                          ';PWD=' + password)

    my_cursor = conn.cursor()
    return my_cursor, conn


def get_user_id():
    user_name = input("Your login in Crowd app: ")

    cursor.execute("SELECT profileID FROM Profile WHERE name = '" + user_name + "'")
    result = cursor.fetchone()
    if result is None:
        print("You are not user of Crowd app, bye!")
        sys.exit()
    return result[0]


def check_if_empty_game(user_id, access_key):
    cursor.execute("SELECT accessKey FROM Game where ownerID = " + str(user_id))

    key = cursor.fetchone()
    while key:
        if int(key[0]) == access_key:
            cursor.execute("SELECT * FROM Game where ownerID = " + str(user_id) +
                           " AND accessKey = " + str(key[0]))
            result = cursor.fetchone()
            if result[1] is None:
                print("You can add new game.")
                return True, result[0]
            else:
                print("This is accessKey for '" + result[1] + "' game.")
                return False, result[0]
        key = cursor.fetchone()

    print("This accessKey doesn't exist, please enter valid accessKey.")
    sys.exit()


def check_access_key(user_id):
    key = input("Enter your access key: ")
    access_key = int(key)
    if access_key == 0:
        print("Wrong key")
        sys.exit()
    return check_if_empty_game(user_id, access_key)


if __name__ == "__main__":
    print("Connecting to database...")
    cursor, connection = get_connection()
    user_id = get_user_id()
    empty_game, game_id = check_access_key(user_id)

    if empty_game is True:
        check_json_file(game_id, cursor, connection)
        connection.commit()
    else:
        print("\nLoading statistics...")
        generate_statistics(user_id, game_id, cursor)
