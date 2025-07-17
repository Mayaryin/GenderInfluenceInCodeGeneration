import sqlite3
import pandas as pd
from scipy import stats

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
                   SELECT llms_prompt_enigneering, gender, COUNT(*)
                   FROM users
                   WHERE users.lastpage > 2
                   GROUP BY llms_prompt_enigneering, gender;'''
                   )
    rows = cursor.fetchall()
    print("Prompt engineering: ", rows)

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
    connection.close()

def make_llm_version_query():
    return '''
                    SELECT llm_version, COUNT(*)
                    FROM conversations
                        GROUP BY llm_version
                        
        '''


def make_average_convo_length_query():

    return '''
                        SELECT gender, AVG(avg_messages_per_convo) AS avg_messages_per_convo_per_gender 
                        FROM ( SELECT user_id, gender, AVG(message_count) AS avg_messages_per_convo 
                               FROM ( SELECT ma.user_id, ma.gender, ma.conversation_id, COUNT(*) AS message_count 
                                      FROM messages_annotated ma 
                                      GROUP BY ma.user_id, ma.gender, ma.conversation_id ) 
                                        user_convo_counts 
                               GROUP BY user_id, gender ) user_avg_counts 
                        GROUP BY gender;
        '''


def get_average_convo_length():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()
    cursor.execute(make_average_convo_length_query())
    rows = cursor.fetchall()
    print("Convo length: ", rows)
    connection.close()

def make_code_blocks_with_convo_id_query():
    return '''
                   SELECT 
            cb.code_block_id,
            cb.message_id,
            cb.code_text,
            cb.language,
            m.conversation_id
        FROM 
            code_blocks cb
        JOIN 
            messages m ON cb.message_id = m.message_id
        JOIN 
            conversations c ON m.conversation_id = c.conversation_id
        WHERE 
            cb.language IS NOT NULL
           '''


def run_t_test_on_gender(df, dependent_variable):
    female = df[df['gender'] == 'Woman (cisgender)'][dependent_variable]
    male = df[df['gender'] == 'Man (cisgender)'][dependent_variable]


    t_stat, p_value = stats.ttest_ind(male, female, equal_var=False)

    print(f"T-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")




