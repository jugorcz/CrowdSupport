import pyodbc
import xlsxwriter

#--------------------------------------------------------
def findPossibleAnswers(questionID, cursor, worksheet, row):
    cursor.execute("SELECT * FROM Answer WHERE questionID = " + str(questionID))
    answers = cursor.fetchall()
    for answer in answers:
        showed = answer[7]
        chosen = answer[6]
        percentage = 0
        content = answer[2]
        if chosen != 0 and showed != 0:
            percentage = 100 * chosen / showed

        print("\t" + content + "\tshowed: " + str(showed) + "\tchosen: " + str(chosen) + "\t" + str(percentage) + "%")

        worksheet.write(row,1, content)
        worksheet.write(row,2, "schowed: " + str(showed))
        worksheet.write(row,3, "chosen:" + str(chosen))
        worksheet.write(row,4, str(percentage) + "%")

        row += 1

    return row


#--------------------------------------------------------
def findAnswersForOpenQeston(questionID, cursor, worksheet, row):
    cursor.execute("SELECT answerID FROM Log WHERE questionID = " + str(questionID))
    answerIDlist = cursor.fetchall()
    for answerID in answerIDlist:
        print("None")

#--------------------------------------------------------
def writeGameProperties(gameID, cursor, worksheet):
    cursor.execute("SELECT * FROM Game WHERE gameID = " + str(gameID))
    game = cursor.fetchone()
    gameName = game[1]
    minLevel = game[2]
    lang = game[3]

    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:D', 10)

    worksheet.write(0,0,"GAME NAME:")
    worksheet.write(1,0,"MINIMUM LEVEL:")
    worksheet.write(2,0,"LANGUAGE:")

    worksheet.write(0,1,gameName)
    worksheet.write(1,1,str(minLevel))
    worksheet.write(2,1,lang)

    return 4 #next row number


#--------------------------------------------------------
def readQuestions(userID, gameID, cursor, worksheet, row):
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(gameID))
    questions = cursor.fetchall()
    questionNumber = 1
    for question in questions:
        questionID = question[0]
        content = question[2]
        typeID = question[3]
        print("\n" + str(questionNumber) + ": " + content)

        row += 1
        worksheet.write(row,0,str(questionNumber) + ": " + content)
        row += 1

        if typeID == 1004: #open answer
            findAnswersForOpenQeston(questionID, cursor, worksheet, row)
        else:
            row = findPossibleAnswers(questionID, cursor, worksheet, row)
        questionNumber += 1

#--------------------------------------------------------
def generateStatistics(userID, gameID, dbCursor):
    cursor = dbCursor
    workbook = xlsxwriter.Workbook('Report.xlsx')
    worksheet = workbook.add_worksheet()

    row = writeGameProperties(gameID, cursor, worksheet)
    readQuestions(userID, gameID, cursor, worksheet, row)

    workbook.close()
    