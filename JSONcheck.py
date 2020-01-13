import json 
import os
import pyodbc


def check_game_properties(content):
    game_name = content["gameName"]
    level = content["minLevel"]
    lang = content["language"].strip()
    if game_name.strip() == "":
        print("Game name can't be empty.")
        return False
    if type(level) is not int:
        print("Minimal level must be number.")
        return False
    if lang != "ENG" and lang != "PL":
        print("Wrong language.")
        return False
    return True


def check_question_properties(question, i):
    text = question["questionText"].strip()
    type_id = question["typeID"]
    image = question["image"]
    default = question["needDefaultAnswer"]
    print("--------------------------\nChecking question " + str(i))
    if text == "":
        print("Empty question text.")
        return False
    if type(type_id) is not int:
        print("Question type ID must be number.")
        return False
    if type_id < 1 or type_id > 3:
        print("Wrong question type ID.")
        return False
    if type_id == 2 and os.path.isfile(image) is False:
        print("Image " + image + " doesn't exist.") 
        return False
    if type(default) is not int or (default != 0 and default != 1):
        print("Wrong default value.")
        return False
    return True


def check_answers(answers, question_type):
    i = 1
    if question_type == 3: # open answer
        return True

    for answer in answers:
        print("\tChecking answer: "+ str(i))
        text = answer["answerText"].strip()
        image = answer["answerImage"].strip()
        text_answer = False
        image_answer = False
        if text != "":
            text_answer = True
        if image != "" and os.path.isfile(image):
            image_answer = True

        if text_answer is False and image_answer is True:
            print("Image answer need also text.")
            return False 
        elif text_answer is False and image_answer is False:
            print("Answer cannot be empty.")
            return False 
        i += 1
    return True


def check_questions(questions):
    i = 1
    for question in questions:
        if check_question_properties(question, i):
            if check_answers(question["answers"], question["typeID"]):
                i += 1
                continue
        return False


def insert_open_answer(cursor, question_id):
    query = "INSERT INTO Answer (questionID, answerText, typeID, answerPic, isDefault, chosen, shown) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?);"

    text = "Open answer"
    cursor.execute(query, question_id, text, 4, None, 0, 0, 0)
    print(query)


def insert_default_answer(cursor, question_id):
    query = "INSERT INTO Answer (questionID, answerText, typeID, answerPic, isDefault, chosen, shown) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?);"

    text = "None of the above"
    cursor.execute(query, question_id, text, 3, None, 1, 0, 0)
    print(query)


def insert_answer(answers, cursor, question_id):
    for answer in answers:
        text = answer["answerText"].strip()
        image = answer["answerImage"]

        if image != "":
            with open(image, 'rb') as f:
                bindata = f.read()
                ablob = pyodbc.Binary(bindata)
        else:
            ablob = None

        query = "INSERT INTO Answer (questionID, answerText, typeID, answerPic, isDefault, chosen, shown) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?);"

        cursor.execute(query, question_id, text, 3, ablob, 0, 0, 0)
        print(query)


def insert_question(questions, cursor, game_id, cnxn):
    for question in questions:
        text = question["questionText"].strip()
        type_id = int(question["typeID"])
        image = question["image"]
        default = question["needDefaultAnswer"]

        type_id -= 1

        if image != "":
            with open(image, 'rb') as f:
                bindata = f.read()
                ablob = pyodbc.Binary(bindata)
        else:
            ablob = None

        query = "INSERT INTO Question (gameID, questionText, typeID, questionImage, defaultAnswer, " \
                "closed, numOfAnswered) VALUES ( ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, game_id, text, type_id, ablob, default, 0, 0)
        print(query)
        cnxn.commit()

        query = "SELECT max(questionID) FROM Question"
        cursor.execute(query)
        question_id = cursor.fetchone()
        print(question_id[0])

        if type_id != 2:
            answers = question["answers"]
            insert_answer(answers, cursor, question_id[0])

            if default == 1:
                insert_default_answer(cursor, question_id[0])
        else:
            insert_open_answer(cursor, question_id[0])


def insert_game(content, cursor, game_id, cnxn):
    game_name = content["gameName"]
    level = content["minLevel"]
    lang = content["language"].strip()
    query = "UPDATE Game SET gameName = '" + game_name + "' where gameID = " + str(game_id)
    print(query)
    cursor.execute(query)

    query = "UPDATE Game SET minLevel = " + str(level) + " where gameID = " + str(game_id)
    cursor.execute(query)

    query = "UPDATE Game SET language = '" + str(lang) + "' where gameID = " + str(game_id)
    cursor.execute(query)

    questions = content["questions"]
    insert_question(questions, cursor, game_id, cnxn)


def check_json_file(game_id, cursor, cnxn):
    with open('game.json') as game_file:

        try:
            content = json.load(game_file)
        except ValueError as error:
            print("\nERROR: json file is not correct.")
            print("message: " + str(error))
            return False

        if check_game_properties(content) is False:
            return False
        questions = content["questions"]
        if check_questions(questions) is False:
            return False
        print("--------------------------\n\nJSON file correct.\n")
        insert_game(content, cursor, game_id, cnxn)
    return True