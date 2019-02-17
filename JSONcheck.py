import json 
import os

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
        if checkQuestionProperties(question, i):
            if checkAnswers(question["answers"]):
                i += 1
                continue
        return False

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
    return True