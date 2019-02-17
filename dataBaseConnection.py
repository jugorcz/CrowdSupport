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

def getUserID():
    userName = raw_input("Your login in Crowd app: ")

    cursor.execute("SELECT profilID FROM Profile WHERE name = '" + userName + "'")
    result = cursor.fetchone()
    if result is None:
        print("You are not user of Crowd app, bye!")
        sys.exit()
    return result[0]

#--------------------------------------------------------
def checkIsEmptyGame(userID, accessKey):
    cursor.execute("SELECT accessKey FROM Game where ownerID = " + str(userID))

    key = cursor.fetchone()
    while key:
        if int(key[0]) == accessKey:
            cursor.execute("SELECT * FROM Game where ownerID = " + str(userID) + " AND accessKey = " + str(key[0]))
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


#--------------------------------------------------------
def checkAccessKey(userID):
    key = raw_input("Enter your access key: ")
    accessKey = int(key)
    if accessKey == 0:
        print("Wrong key")
        sys.exit()
    return checkIsEmptyGame(userID, accessKey)


#--------------------------------------------------------
import pyodbc
import sys
import os
from JSONcheck import checkJSONfile
from staticticsGenerate import generateStatistics

print("Connecting to database...")

cursor = getConnection()
userID = getUserID()
emptyGame, gameID = checkAccessKey(userID)

if emptyGame is True:
    checkJSONfile(gameID)
else:
    print("\nLoading statistics...")
    generateStatistics(userID, gameID, cursor)
