import sqlite3

def get_user_stats():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()
    cursor.execute('''
                   SELECT gender, COUNT(*) FROM users WHERE users.lastpage > 2 GROUP BY gender;'''
                   )
    rows = cursor.fetchall()
    print("Gender: ", rows)

    cursor.execute('''
                   SELECT age, COUNT(*)
                   FROM users
                   WHERE users.lastpage > 2
                   GROUP BY age;'''
                   )
    rows = cursor.fetchall()
    print("Age: ", rows)

    cursor.execute('''
                   SELECT education, COUNT(*)
                   FROM users
                   WHERE users.lastpage > 2
                   GROUP BY education;'''
                   )
    rows = cursor.fetchall()
    print("Education: ", rows)

    cursor.execute('''
                   SELECT status, COUNT(*)
                   FROM users
                   WHERE users.lastpage > 2
                   GROUP BY status;'''
                   )
    rows = cursor.fetchall()
    print("Status: ", rows)

    cursor.execute('''
                   SELECT education, COUNT(*)
                   FROM users
                   WHERE users.lastpage > 2
                   GROUP BY education;'''
                   )
    rows = cursor.fetchall()
    print("Education: ", rows)


    connection.close()

def get_conversation_stats():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute('''
                   SELECT mode, COUNT(*)
                   FROM conversations
                   GROUP BY mode

                   ''')
    rows = cursor.fetchall()
    print("Modes: ", rows)

    cursor.execute('''
                    SELECT llm_version, COUNT(*)
                    FROM conversations
                        GROUP BY llm_version
                        
        ''')
    rows = cursor.fetchall()
    print("Models: ", rows)

