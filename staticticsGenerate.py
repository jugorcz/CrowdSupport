import pyodbc

#--------------------------------------------------------
def findPossibleAnswers(questionID, cursor):
    cursor.execute("SELECT * FROM Answer WHERE questionID = " + str(questionID))
    answers = cursor.fetchall()
    for answer in answers:
        showed = answer[7]
        chosen = answer[6]
        percentage = 0
        if chosen != 0 and showed != 0:
            percentage = 100 * chosen / showed
        print("\t" + str(answer[2]) + "\tshowed: " + str(showed) + "\tchosen: " + str(chosen) + "\t" + str(percentage) + "%")


#--------------------------------------------------------
def findAnswersForOpenQeston(questionID, cursor):
    cursor.execute("SELECT answerID FROM Log WHERE questionID = " + str(questionID))
    answerIDlist = cursor.fetchall()
    for answerID in answerIDlist:
        print("None")


#--------------------------------------------------------
def generateStatistics(userID, gameID, dbCursor):
    cursor = dbCursor
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(gameID))
    questions = cursor.fetchall()
    questionNumber = 1
    for question in questions:
        questionID = question[0]
        content = question[2]
        typeID = question[3]
        print("\n" + str(questionNumber) + ": " + content)
        if typeID == 1004: #open answer
            findAnswersForOpenQeston(questionID, cursor)
        else:
            findPossibleAnswers(questionID, cursor)
        questionNumber += 1