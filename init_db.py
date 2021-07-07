import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


cur.execute("INSERT INTO usersdb (username, userrole, usertoken, userpassword) VALUES (?, ?, ?, ?)",
            ('jp', 'admin', 'notatoken', 'notapassword')
            )

connection.commit()
connection.close()