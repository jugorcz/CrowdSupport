import pyodbc
print("Hello World")

server = 'den1.mssql8.gear.host'
database = 'crowd'
username = 'crowd'
password = 'Ng65JF4j79-!'
driver= '{ODBC Driver 17 for SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

cursor = cnxn.cursor()

cursor.execute("SELECT * FROM GAME")
row = cursor.fetchone()
while row:
    print (str(row[0]) + " " + str(row[1]))
    row = cursor.fetchone()