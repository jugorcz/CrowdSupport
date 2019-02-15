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
    print("Your login in Crowd app:")
    userName = raw_input()

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
            print("key found!")
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
    print("Enter your access key: ")
    key = raw_input()
    accessKey = int(key)
    if accessKey == 0:
        print("Wrong key")
        sys.exit()
    return checkIsEmptyGame(userID, accessKey)

#--------------------------------------------------------
def findPossibleAnswers(questionID, cursor):
    cursor.execute("SELECT * FROM Answer WHERE questionID = " + str(questionID))
    answers = cursor.fetchall()
    for answer in answers:
        showed = answer[9]
        chosen = answer[8]
        percentage = 0
        if chosen != 0 and showed != 0:
            percentage = 100 * chosen / showed
        print("\t" + str(answer[2]) + "\tshowed: " + str(answer[9]) + "\tchosen: " + str(answer[8]) + "\t" + str(percentage) + "%")



#--------------------------------------------------------
def generateStatistics(userID, gameID, cursor):
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(gameID))
    questions = cursor.fetchall()
    questionNumber = 1
    for question in questions:
        print("\n" + str(questionNumber) + ": " + question[2])
        findPossibleAnswers(question[0], cursor)
        questionNumber += 1




#--------------------------------------------------------
import pyodbc
import sys
cursor = getConnection()
userID = getUserID()
emptyGame, gameID = checkAccessKey(userID)

if emptyGame is True:
    print("Add new game")
else:
    print("Please wait, statistics are loaded.")
    generateStatistics(userID, gameID, cursor)
