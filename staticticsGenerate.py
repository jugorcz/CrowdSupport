import pyodbc
import io
from PIL import Image
import xlsxwriter

#--------------------------------------------------------
def findPossibleAnswers(questionID, cursor, worksheet, row, workbook):
    cursor.execute("SELECT * FROM Answer WHERE questionID = " + str(questionID) + " ORDER BY 100*chosen/(showed + 1) DESC")
    answers = cursor.fetchall()
    first = True
    answerNumber = 1
    for answer in answers:
        showed = answer[7]
        chosen = answer[6]
        percentage = 0
        content = answer[2]
        default = answer[5]
        image = answer[4]

        rows = 1

        if default == 1:
            continue

        if image is not None:
            img = Image.open(io.BytesIO(image))
            imageFileName = "img/a" + str(answerNumber) + ".png"
            img.save(imageFileName)
            width, height = img.size
            scale = 60.0/float(height)
            #worksheet.set_row(row+2, 20)  # Set the height of Row 1 to 20.
            worksheet.insert_image(row+1, 1, imageFileName, {'x_scale': scale, 'y_scale': scale})
            rows = 5

        if chosen != 0 and showed != 0:
            percentage = 100 * chosen / showed

        print("\tAnswer: " + str(answerNumber))

        if first:
            bold = workbook.add_format({'bold': True})
            first = False
        else:
            bold = workbook.add_format({'bold': False})

        worksheet.write(row,1, content, bold)
        worksheet.write(row,2, "showed: " + str(showed), bold)
        worksheet.write(row,3, "chosen:" + str(chosen), bold)
        worksheet.write(row,4, str(percentage) + "%", bold)

        row += rows
        answerNumber += 1

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

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)

    worksheet.write(0,0,"game : " + str(gameName))
    worksheet.write(1,0,"min level: " + str(minLevel))
    worksheet.write(2,0,"language: " + str(lang))

    return 4 #next row number


#--------------------------------------------------------
def readQuestions(userID, gameID, cursor, worksheet, row, workbook):
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(gameID))
    questions = cursor.fetchall()
    questionNumber = 1
    for question in questions:
        questionID = question[0]
        content = question[2]
        typeID = question[3]
        image = question[5]
        closed = question[7]
        rows = 1
        if image is not None:
            img = Image.open(io.BytesIO(image))
            imageFileName = "img/q" + str(questionNumber) + ".png"
            img.save(imageFileName)
            width, height = img.size
            #print(width)
            #print(height)
            scale = 95.0/float(height)
            #print(scale)
            worksheet.set_row(row+2, 20)  # Set the height of Row 1 to 20.
            worksheet.insert_image(row+2, 0, imageFileName, {'x_scale': scale, 'y_scale': scale})
            rows = 2

        print("\nQuestion: " + str(questionNumber))

        row += 1
        if closed == 1:
            cell_format = workbook.add_format({'bg_color': '99ff66'}) #green
            worksheet.write(row,1,"Found proper answer", cell_format)
        else:
            cell_format = workbook.add_format({'bg_color': 'ff9966'}) #red
            worksheet.write(row,1,"", cell_format)

        worksheet.write(row,0,str(questionNumber) + ": " + content, cell_format)
        
        worksheet.write(row,2,"", cell_format)
        worksheet.write(row,3,"", cell_format)
        worksheet.write(row,4,"", cell_format)

        row += 1

        if typeID == 1004: #open answer
            findAnswersForOpenQeston(questionID, cursor, worksheet, row)
        else:
            row = findPossibleAnswers(questionID, cursor, worksheet, row, workbook)
        questionNumber += 1
        row += rows

#--------------------------------------------------------
def generateStatistics(userID, gameID, dbCursor):
    cursor = dbCursor
    workbook = xlsxwriter.Workbook('Report.xlsx')
    worksheet = workbook.add_worksheet()

    row = writeGameProperties(gameID, cursor, worksheet)
    readQuestions(userID, gameID, cursor, worksheet, row, workbook)

    print("\nDone, check report.")

    workbook.close()
    