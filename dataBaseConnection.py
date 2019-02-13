def getConnection():
    server = 'den1.mssql8.gear.host'
    database = 'crowd'
    username = 'crowd'
    password = 'Ng65JF4j79-!'
    driver= '{ODBC Driver 17 for SQL Server}'

    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

    cursor = cnxn.cursor()
    return cursor


#--------------------------------------------------------
def findUser(userName):
    cursor.execute("SELECT profilID FROM Profile WHERE name = '" + userName + "'")
    result = cursor.fetchone()
    if result is None:
        print("You are not user of Crowd app, bye!")
        sys.exit()
    else:
        print("user id: " + str(result[0]))
    return result[0]

#--------------------------------------------------------
def findAccessKey(userID, accessKey):
    cursor.execute("SELECT accessKey FROM Game where ownerID = " + str(userID))

    key = cursor.fetchone()
    while key:
        if int(key[0]) == accessKey:
            print("key found!")
            cursor.execute("SELECT * FROM Game where ownerID = " + str(userID) + " AND accessKey = " + str(key[0]))
            result = cursor.fetchone()
            if result[1] is None:
                print("You can add new game.")
                return True, True
            else:
                print("This accessKey was already used for '" + result[1] + "' game.")
                return True, False
        key = cursor.fetchone()
    return False, False

#--------------------------------------------------------

def getUserData():
    print("User login:")
    userName = raw_input()
    print("Hello " + userName)
    userID = findUser(userName)

    print("Enter your access key: ")
    key = raw_input()
    accessKey = int(key)
    if accessKey == 0:
        print("Wrong key")
        sys.exit()

    print("Your key: " + str(accessKey))
    keyEgsists, gameisEmpty = findAccessKey(userID, accessKey)


#--------------------------------------------------------
import pyodbc
import sys
cursor = getConnection()
getUserData()
