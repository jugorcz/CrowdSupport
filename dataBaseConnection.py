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
def findPossibleAnswers(questionID):
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
def findAnswersForOpenQeston(questionID):
    cursor.execute("SELECT answerID FROM Log WHERE questionID = " + str(questionID))
    answerIDlist = cursor.fetchall()
    for answerID in answerIDlist:
        print("None")


#--------------------------------------------------------
def generateStatistics(userID, gameID):
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(gameID))
    questions = cursor.fetchall()
    questionNumber = 1
    for question in questions:
        questionID = question[0]
        content = question[2]
        typeID = question[3]
        print("\n" + str(questionNumber) + ": " + content)
        if typeID == 1004: #open answer
            findAnswersForOpenQeston(questionID)
        else:
            findPossibleAnswers(questionID)
        questionNumber += 1


#--------------------------------------------------------
def checkGameProperties(content):
    gameName = content["gameName"]
    description = content["gameDescription"]
    level = content["minLevel"]
    lang = content["language"].strip()
    if gameName.strip() == "":
        print("Game name can't be empty.")
        return False
    if type(level) is not int:
        print("Minimal level must be number.")
        return False
    if lang != "ENG" and lang != "PL":
        print("Wrong language.")
        return False
    return True


#--------------------------------------------------------
def checkQuestionProperties(question, i):
    text = question["questionText"].strip()
    typeID = question["typeID"]
    image = question["image"]
    default = question["needDefaultAnswer"]
    print("--------------------------\nChecking question " + str(i))
    if text == "":
        print("Empty question text.")
        return False
    if type(typeID) is not int:
        print("Question type ID must be number.")
        return False
    if typeID < 1 or typeID > 3:
        print("Wrong question type ID.")
        return False
    if typeID == 2 and os.path.isfile(image) is False:
        print("Image " + image + " doesn't exist.") 
        return False
    if type(default) is not int or (default != 0 and default != 1):
        print("Wrong default value.")
        return False
    return True

#--------------------------------------------------------
def checkAnswers(answers):
    i = 1
    for answer in answers:
        print("\tChecking answer: "+ str(i))
        text = answer["answerText"].strip()
        image = answer["answerImage"].strip()
        textAnswer = False
        imageAnswer = False
        if text != "":
            textAnswer = True
        if image != "" and os.path.isfile(image):
            imageAnswer = True

        if textAnswer and imageAnswer:
            print("\tAnswer can be text OR image.")
            return False 
        if textAnswer is False and imageAnswer is False:
            print("\tEmpty answer.")
            return False 
        i += 1
    return True


#--------------------------------------------------------
def checkQuestions(questions):
    i = 1
    for question in questions:
        if checkQuestionProperties(question, i) is False:
            return False
        if checkAnswers(question["answers"]) is False:
            return False
        i += 1
    return True

#--------------------------------------------------------
def checkJSONfile(gameID):
    with open('game.json') as gameFile:
        content = json.load(gameFile)
        if checkGameProperties(content) is False:
            return False
        questions = content["questions"]
        if checkQuestions(questions) is False:
            return False
        print("--------------------------\nJSON file correct.")


#--------------------------------------------------------
import pyodbc
import sys
import json 
import os

print("Connecting to database...")

cursor = getConnection()
userID = getUserID()
emptyGame, gameID = checkAccessKey(userID)

if emptyGame is True:
    checkJSONfile(gameID)
else:
    print("\nLoading statistics...")
    generateStatistics(userID, gameID)
