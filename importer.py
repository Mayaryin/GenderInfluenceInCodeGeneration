import sqlite3
import pandas as pd


def import_raw_data_to_database(filename):
    df = pd.read_csv(filename)
    print("Columns in CSV:", df.columns)
    connection = sqlite3.connect("giicg.db")
    df.to_sql("raw_data", connection, if_exists="replace")
    connection.close()


def create_working_data_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Deleting table")
    cursor.execute("DROP TABLE IF EXISTS working_data")

    print("Creating table schema with PRIMARY KEY")
    cursor.execute('''
        CREATE TABLE working_data (
            user_id INTEGER PRIMARY KEY,
            lastpage INTEGER,
            seed TEXT,
            age TEXT,
            education TEXT,
            status TEXT,
            study_field TEXT,
            study_year TEXT,
            work_field TEXT,
            work_exp_years TEXT,
            context_work TEXT,
            context_university TEXT,
            context_personal TEXT,
            context_other TEXT,
            usage_frequency TEXT,
            eng_native TEXT,
            eng_level TEXT,
            gender TEXT,

            c1_mode TEXT,
            c1_text TEXT,
            c1_share_link TEXT,
            c1_llm_version TEXT,
            c1_satisfaction TEXT,
            c1_explain_satisfaction TEXT,
            c1_rated_complexity TEXT,

            c2_mode TEXT,
            c2_text TEXT,
            c2_share_link TEXT,
            c2_llm_version TEXT,
            c2_satisfaction TEXT,
            c2_explain_satisfaction TEXT,
            c2_rated_complexity TEXT,

            c3_mode TEXT,
            c3_text TEXT,
            c3_share_link TEXT,
            c3_llm_version TEXT,
            c3_satisfaction TEXT,
            c3_explain_satisfaction TEXT,
            c3_rated_complexity TEXT,

            c4_mode TEXT,
            c4_text TEXT,
            c4_share_link TEXT,
            c4_llm_version TEXT,
            c4_satisfaction TEXT,
            c4_explain_satisfaction TEXT,
            c4_rated_complexity TEXT,

            c5_mode TEXT,
            c5_text TEXT,
            c5_share_link TEXT,
            c5_llm_version TEXT,
            c5_satisfaction TEXT,
            c5_explain_satisfaction TEXT,
            c5_rated_complexity TEXT,

            llms_helpful TEXT,
            llms_enjoy TEXT,
            llms_go_back TEXT,
            llms_faster TEXT,
            llms_slower TEXT,
            llms_prompt_enigneering TEXT,
            llms_approach TEXT,
            llms_describe_approach TEXT,
            llms_ethical_concerns TEXT,
            llms_ec_bias TEXT,
            llms_ec_discrimination TEXT,
            llms_ec_skill_loss TEXT,
            llms_ec_learn_less TEXT,
            llms_ec_diversity_loss TEXT,
            llms_ec_other TEXT,
            llms_other_concerns TEXT,
            llms_other_toughts TEXT
        );
    ''')

    print("Inserting data into table")
    cursor.execute('''
        INSERT INTO working_data (
            user_id, lastpage, seed,
            age, education, status, study_field, study_year, work_field, work_exp_years,
            context_work, context_university, context_personal, context_other,
            usage_frequency, eng_native, eng_level, gender,

            c1_mode, c1_text, c1_share_link, c1_llm_version, c1_satisfaction, c1_explain_satisfaction, c1_rated_complexity,
            c2_mode, c2_text, c2_share_link, c2_llm_version, c2_satisfaction, c2_explain_satisfaction, c2_rated_complexity,
            c3_mode, c3_text, c3_share_link, c3_llm_version, c3_satisfaction, c3_explain_satisfaction, c3_rated_complexity,
            c4_mode, c4_text, c4_share_link, c4_llm_version, c4_satisfaction, c4_explain_satisfaction, c4_rated_complexity,
            c5_mode, c5_text, c5_share_link, c5_llm_version, c5_satisfaction, c5_explain_satisfaction, c5_rated_complexity,

            llms_helpful, llms_enjoy, llms_go_back, llms_faster, llms_slower,
            llms_prompt_enigneering, llms_approach, llms_describe_approach,
            llms_ethical_concerns, llms_ec_bias, llms_ec_discrimination, llms_ec_skill_loss,
            llms_ec_learn_less, llms_ec_diversity_loss, llms_ec_other, llms_other_concerns,
            llms_other_toughts
        )
        SELECT
            "Response ID", "Last page", "Seed",
            "Please select y.. ", "What is your hi.. ", "What is your st.. ", "What is your fi.. ", "In which year a.. ", "What is your fi.. .1", "How many years .. ",
            "In what context..  [At work]", "In what context..  [At university]", "In what context..  [Personal projects]", "In what context..  [Other]",
            "How often do yo.. ", "Is English your.. ", "How would you d.. ", "Which of the fo.. ",

            "How do you want.. ", "Copy the conver.. ", "Copy the share .. ", "What LLM versio.. ", "How would you r.. ", "Can you explain.. ", "How complex wou.. ",
            "How do you want.. .1", "Copy the conver.. .1", "Copy the share .. .1", "What LLM versio.. .1", "How would you r.. .1", "Can you explain.. .1", "How complex wou.. .1",
            "How do you want.. .2", "Copy the conver.. .2", "Copy the share .. .2", "What LLM versio.. .2", "How would you r.. .2", "Can you explain.. .2", "How complex wou.. .2",
            "How do you want.. .3", "Copy the conver.. .3", "Copy the share .. .3", "What LLM versio.. .3", "How would you r.. .3", "Can you explain.. .3", "How complex wou.. .3",
            "How do you want.. .4", "Copy the conver.. .4", "Copy the share .. .4", "What LLM versio.. .4", "How would you r.. .4", "Can you explain.. .4", "How complex wou.. .4",

            "LLMs are helpfu.. ", "I enjoy using L.. ", "I would like to.. ", "I have become f.. ", "I have become s.. ",
            "I am employing .. ", "My way to appro.. ", "Can you describ.. ", "I have ethical .. ",
            "Can you specify..  [LLMs can reprod.. ]", "Can you specify..  [LLMs can reprod.. ].1", "Can you specify..  [LLMs can lead t.. ]",
            "Can you specify..  [LLM users can l.. ]", "Can you specify..  [LLMs can lead t.. ].1", "Can you specify..  [Other:]",
            "What other conc.. ", "Do you have any.. "
        FROM raw_data
        WHERE "Last page" > 0;
    ''')

    connection.commit()
    connection.close()
    print("Table created with PRIMARY KEY and data inserted.")

def clean_up_database():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()
    print("Deleting tables")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS conversations")
    cursor.execute("DROP TABLE IF EXISTS messages")
    cursor.execute("DROP TABLE IF EXISTS code_blocks")
    connection.close()



def create_user_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")  # Enable FK constraints

    print("Deleting tables")
    cursor.execute("DROP TABLE IF EXISTS users")

    print("Creating table schema for user table with PRIMARY KEY")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lastpage INTEGER,
            seed TEXT,
            
            age TEXT,
            education TEXT,
            status TEXT,
            study_field TEXT,
            study_year TEXT,
            work_field TEXT,
            work_exp_years TEXT,
            context_work TEXT,
            context_university TEXT,
            context_personal TEXT,
            context_other TEXT,
            usage_frequency TEXT,
            eng_native TEXT,
            eng_level TEXT,
            gender TEXT,
            
            llms_helpful TEXT,
            llms_enjoy TEXT,
            llms_go_back TEXT,
            llms_faster TEXT,
            llms_slower TEXT,
            llms_prompt_enigneering TEXT,
            llms_approach TEXT,
            llms_describe_approach TEXT,
            llms_ethical_concerns TEXT,
            llms_ec_bias TEXT,
            llms_ec_discrimination TEXT,
            llms_ec_skill_loss TEXT,
            llms_ec_learn_less TEXT,
            llms_ec_diversity_loss TEXT,
            llms_ec_other TEXT,
            llms_other_concerns TEXT,
            llms_other_toughts TEXT
        );
    ''')
    print("Inserting data into table")
    cursor.execute('''
               INSERT INTO users (
                   user_id, lastpage, seed,
                   
                     age, education, status, study_field, study_year, work_field,
                     work_exp_years,
                     context_work, context_university, context_personal, context_other,
                     usage_frequency, eng_native, eng_level, gender,
                     
                     llms_helpful, llms_enjoy, llms_go_back, llms_faster, llms_slower,
                     llms_prompt_enigneering, llms_approach, llms_describe_approach,
                     llms_ethical_concerns, llms_ec_bias, llms_ec_discrimination,
                     llms_ec_skill_loss,
                     llms_ec_learn_less, llms_ec_diversity_loss, llms_ec_other,
                     llms_other_concerns,
                     llms_other_toughts
               )
               SELECT 
                   user_id, lastpage, seed,
                   age, education, status, study_field, study_year, work_field,
                   work_exp_years,
                   context_work, context_university, context_personal, context_other,
                   usage_frequency, eng_native, eng_level, gender,  
                   llms_helpful, llms_enjoy, llms_go_back, llms_faster, llms_slower,
                   llms_prompt_enigneering, llms_approach, llms_describe_approach,
                   llms_ethical_concerns, llms_ec_bias, llms_ec_discrimination,
                   llms_ec_skill_loss,
                     llms_ec_learn_less, llms_ec_diversity_loss, llms_ec_other,
                     llms_other_concerns,
                     llms_other_toughts
               FROM working_data
               ''')
    connection.commit()
    connection.close()
    print("Table created with PRIMARY KEY and data inserted.")

def create_conversations_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")  # Enable FK constraints

    print("Deleting tables")
    cursor.execute("DROP TABLE IF EXISTS conversations")

    print("Creating table schema for conversations table with PRIMARY KEY")
    cursor.execute('''
                  CREATE TABLE conversations (
    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mode TEXT,
    text TEXT,
    share_link TEXT,
    llm_version TEXT,
    satisfaction TEXT,
    explain_satisfaction TEXT,
    rated_complexity INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

                   ''')

    # Load the raw data table into a DataFrame
    df = pd.read_sql_query("SELECT * FROM working_data", connection)

    # Define conversation prefixes
    convo_nums = [1, 2, 3, 4, 5]
    convo_data = []

    for c in convo_nums:
        sub_df = pd.DataFrame({
            'user_id': df['user_id'],
            'mode': df[f'c{c}_mode'],
            'text': df[f'c{c}_text'],
            'share_link': df[f'c{c}_share_link'],
            'llm_version': df[f'c{c}_llm_version'],
            'satisfaction': df[f'c{c}_satisfaction'],
            'explain_satisfaction': df[f'c{c}_explain_satisfaction'],
            'rated_complexity': df[f'c{c}_rated_complexity']
        })
        # Remove empty conversations
        sub_df = sub_df[sub_df['text'].notna() | sub_df['share_link'].notna()]
        convo_data.append(sub_df)

    # Combine all conversation DataFrames
    conversations_df = pd.concat(convo_data, ignore_index=True)

    conversations_df.to_sql('conversations', connection, if_exists='append', index=False)

    connection.commit()
    connection.close()
    print("Table created with PRIMARY KEY and data inserted.")

def create_messages_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")  # Enable FK constraints

    print("Deleting tables")
    cursor.execute("DROP TABLE IF EXISTS messages")

    print("Creating table schema for messages table with PRIMARY KEY")
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS messages(
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    message_text TEXT NOT NULL,
                    model_version TEXT,
                    message_order INTEGER NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
                   );

                   ''')
    connection.commit()
    connection.close()
    print("Table created with PRIMARY KEY")

def create_code_blocks_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")  # Enable FK constraints

    print("Deleting tables")
    cursor.execute("DROP TABLE IF EXISTS code_blocks")

    print("Creating table schema for code blocks table with PRIMARY KEY")
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS code_blocks (
                    code_block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    code_text TEXT NOT NULL,
                    language TEXT,  
                    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
                    );
                   ''')
    connection.commit()
    connection.close()
    print("Table created with PRIMARY KEY")








