import io
from PIL import Image
import xlsxwriter


def find_possible_answers(question_id, cursor, worksheet, row, workbook):
    cursor.execute("SELECT * FROM Answer WHERE questionID = " +
                   str(question_id) + " ORDER BY 100*chosen/(shown + 1) DESC")
    answers = cursor.fetchall()
    first = True
    answer_number = 1
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
            image_file_name = "img/a" + str(answer_number) + ".png"
            img.save(image_file_name)
            width, height = img.size
            scale = 60.0/float(height)
            # worksheet.set_row(row+2, 20)  # Set the height of Row 1 to 20.
            worksheet.insert_image(row+1, 1, image_file_name, {'x_scale': scale, 'y_scale': scale})
            # os.remove(imageFileName)
            rows = 5

        if chosen != 0 and showed != 0:
            percentage = 100 * chosen / showed

        print("\tAnswer: " + str(answer_number))

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
        answer_number += 1

    return row


def find_answers_for_open_qestion(question_id, cursor, worksheet, row):
    cursor.execute("SELECT * FROM Log WHERE questionID = " + str(question_id))
    logs_dictionary = dict()
    logs = cursor.fetchall()
    for log in logs:
        answer = log[4]
        if answer is None:
            continue

        if answer in logs_dictionary:
            logs_dictionary[answer] += 1
        else: 
            logs_dictionary[answer] = 1

    for answer in logs_dictionary:
        worksheet.write(row,1, answer)
        worksheet.write(row,2, "appeared: " + str(logs_dictionary[answer]))
        print(str(answer) + " appeared: " + str(logs_dictionary[answer]))
        row += 1
    return row


def write_game_properties(game_id, cursor, worksheet):
    cursor.execute("SELECT * FROM Game WHERE gameID = " + str(game_id))
    game = cursor.fetchone()
    game_name = game[1]
    min_level = game[2]
    lang = game[3]

    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)

    worksheet.write(0,0,"game : " + str(game_name))
    worksheet.write(1,0,"min level: " + str(min_level))
    worksheet.write(2,0,"language: " + str(lang))

    return 4  # next row number


def read_questions(game_id, cursor, worksheet, row, workbook):
    cursor.execute("SELECT * FROM Question WHERE gameID = " + str(game_id))
    questions = cursor.fetchall()
    questions_number = 1
    for question in questions:
        question_id = question[0]
        content = question[2]
        type_id = question[6]
        image = question[4]
        closed = question[7]
        rows = 1
        if image is not None:
            img = Image.open(io.BytesIO(image))
            image_file_name = "img/q" + str(questions_number) + ".png"
            img.save(image_file_name)
            width, height = img.size
            # print(width)
            # print(height)
            scale = 95.0/float(height)
            # print(scale)
            worksheet.set_row(row+2, 20)  # Set the height of Row 1 to 20.
            worksheet.insert_image(row+2, 0, image_file_name, {'x_scale': scale, 'y_scale': scale})
            rows = 2

        print("\nQuestion: " + str(questions_number))

        row += 1
        if closed == 1:
            cell_format = workbook.add_format({'bg_color': '99ff66'}) # green
            worksheet.write(row, 1, "Found proper answer", cell_format)
        else:
            cell_format = workbook.add_format({'bg_color': 'ff9966'}) # red
            worksheet.write(row, 1, "", cell_format)

        worksheet.write(row, 0, str(questions_number) + ": " + content, cell_format)
        
        worksheet.write(row, 2, "", cell_format)
        worksheet.write(row, 3, "", cell_format)
        worksheet.write(row, 4, "", cell_format)

        row += 1

        if type_id == 1004: # open answer
            row = find_answers_for_open_qestion(question_id, cursor, worksheet, row)
        else:
            row = find_possible_answers(question_id, cursor, worksheet, row, workbook)
        questions_number += 1
        row += rows


def generate_statistics(user_id, game_id, db_cursor):
    cursor = db_cursor
    workbook = xlsxwriter.Workbook('Report.xlsx')
    worksheet = workbook.add_worksheet()

    row = write_game_properties(game_id, cursor, worksheet)
    read_questions(game_id, cursor, worksheet, row, workbook)
    print("\nDone, check report.")

    workbook.close()
