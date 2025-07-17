import sqlite3

import importer
import prompt_parser
import scraper
import statistics
import pandas as pd

pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.width", None)        # Don’t wrap lines (use full width)
pd.set_option("display.max_colwidth", None) # Show full content in each cell


def prepare_database():
    importer.create_working_data_table()
    importer.clean_up_database()
    importer.create_user_table()
    importer.create_conversations_table()
    importer.create_messages_table()
    importer.create_code_blocks_table()
    scraper.populate_tables()
    importer.create_gender_annotated_messages_table()
    importer.assign_most_used_model_versions()
    return 0


def main():
    # prepare_database()
    # prompt_parser.populate_table()

    #statistics.get_user_stats()
    #statistics.get_conversation_stats()

    #statistics.get_average_convo_length()
    #conn= sqlite3.connect('giicg.db')

    #query = """
    # SELECT user_id, gender, AVG(message_count) AS avg_messages_per_convo
      #                         FROM ( SELECT ma.user_id, ma.gender, ma.conversation_id, COUNT(*) AS message_count
       #                               FROM messages_annotated ma
        #                              GROUP BY ma.user_id, ma.gender, ma.conversation_id )
         #                               user_convo_counts
          #                     GROUP BY user_id, gender"""

    #df = pd.read_sql_query(query, conn)
    #print(df)

    #statistics.run_t_test_on_gender(df, "avg_messages_per_convo")






if __name__ == '__main__':
    main()