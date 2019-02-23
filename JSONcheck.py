import json 
import os
import pyodbc
from PIL import Image
import io

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
def checkAnswers(answers, questionType):
    i = 1

    if questionType == 3: #open answer
        return True

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

        if textAnswer is False and imageAnswer is True:
            print("Image answer need also text.")
            return False 
        elif textAnswer is False and imageAnswer is False:
            print("Answer cannot be empty.")
            return False 
        i += 1
    return True


#--------------------------------------------------------
def checkQuestions(questions):
    i = 1
    for question in questions:
        if checkQuestionProperties(question, i):
            if checkAnswers(question["answers"], question["typeID"]):
                i += 1
                continue
        return False

#--------------------------------------------------------
def insertOpenAnswer(cursor, questionID):
    query = "INSERT INTO Answer (questionID, answerText, typeID, answerImage, defaultAnswer, chosen, showed) VALUES (?, ?, ?, ?, ?, ?, ?);"

    text = "Open answer"
    cursor.execute(query, questionID, text, 1005, None, 0, 0, 0)
    print(query)

#--------------------------------------------------------
def insertDefaultAnswer(cursor, questionID):
    query = "INSERT INTO Answer (questionID, answerText, typeID, answerImage, defaultAnswer, chosen, showed) VALUES (?, ?, ?, ?, ?, ?, ?);"

    text = "None of the above"
    cursor.execute(query, questionID, text, 3, None, 1, 0, 0)
    print(query)


#--------------------------------------------------------
def insertAnswer(answers, cursor, questionID):
    for answer in answers:
        text = answer["answerText"].strip()
        image = answer["answerImage"]

        if image != "":
            with open(image, 'rb') as f:
                bindata = f.read()
                ablob = pyodbc.Binary(bindata)
        else:
            ablob = None

        query = "INSERT INTO Answer (questionID, answerText, typeID, answerImage, defaultAnswer, chosen, showed) VALUES (?, ?, ?, ?, ?, ?, ?);"

        cursor.execute(query, questionID, text, 3, ablob, 0, 0 ,0)
        print(query)


#--------------------------------------------------------
def insertQuestion(questions, cursor, gameID, cnxn):
    for question in questions:
        text = question["questionText"].strip()
        typeID = int(question["typeID"])
        image = question["image"]
        default = question["needDefaultAnswer"]

        if typeID == 2:
            typeID = 1003 #image
        elif typeID == 3:
            typeID = 1004 #open

        if image != "":
            with open(image, 'rb') as f:
                bindata = f.read()
                ablob = pyodbc.Binary(bindata)
        else:
            ablob = None

        query = "INSERT INTO Question (gameID, questionText, typeID, questionImage, defaultAnswer, closed) VALUES ( ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, gameID, text, typeID, ablob, default, 0)
        print(query)
        cnxn.commit()

        query = "SELECT max(questionID) FROM Question"
        cursor.execute(query)
        questionID = cursor.fetchone()
        print(questionID[0])

        if typeID != 1004:
            answers = question["answers"]
            insertAnswer(answers, cursor, questionID[0])

            if default == 1:
                insertDefaultAnswer(cursor, questionID[0])
        else:
            insertOpenAnswer(cursor, questionID[0])


#--------------------------------------------------------
def insertGame(content, cursor, gameID, cnxn):
    gameName = content["gameName"]
    description = content["gameDescription"]
    level = content["minLevel"]
    lang = content["language"].strip()
    description = content["gameDescription"]
    query = "UPDATE Game SET gameName = '" + gameName + "' where gameID = " + str(gameID)
    print(query)
    cursor.execute(query)

    query = "UPDATE Game SET minLevel = " + str(level) + " where gameID = " + str(gameID)
    cursor.execute(query)

    query = "UPDATE Game SET language = '" + str(lang) + "' where gameID = " + str(gameID)
    cursor.execute(query)

    query = "UPDATE Game SET description = '" + str(description) + "' where gameID = " + str(gameID)
    cursor.execute(query)

    questions = content["questions"]
    insertQuestion(questions, cursor, gameID, cnxn)


#--------------------------------------------------------
def checkJSONfile(gameID, cursor, cnxn):
    with open('game.json') as gameFile:

        try:
            content = json.load(gameFile)
        except ValueError as error:
            print("\nERROR: json file is not correct.")
            print("message: " + str(error))
            return False

        if checkGameProperties(content) is False:
            return False
        questions = content["questions"]
        if checkQuestions(questions) is False:
            return False
        print("--------------------------\n\nJSON file correct.\n")
        insertGame(content, cursor, gameID, cnxn)
    return True