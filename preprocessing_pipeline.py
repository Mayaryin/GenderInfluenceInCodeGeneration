"""
Data Loader

This module is responsible for importing raw CSV data into a structured relational database. It performs the following tasks:

- Imports the raw CSV file into a table named `raw_data`.
- Creates a relational nested schema with the following tables: `users`, `conversations`, `messages`, and `code_blocks`.
- Scrapes conversations provided via a share link and fills the `messages` table with the scraped content.
- Separates the conversations into user messages and LLM messages, annotating them with the programming language used.
- Parses and separates each code block from the LLM messages, inserting them into the `code_blocks` table.
- Separates each user message into conversational parts, code sections, and other components.

This file is not a jupyter notebook since playwright's scraping interferes with the notebook execution flow.

Dependencies:
- `helpers` module for importing, parsing, and scraping.
- `sqlite3` for database operations.
- `python-dotenv` for loading environment variables.
"""

from helpers import importer, prompt_parser
import sqlite3
from dotenv import load_dotenv
import os

from helpers.private import manual_importer

load_dotenv()
FILENAME =  os.getenv('SURVEY_PATH')
print(FILENAME)


def prepare_database(conn, cur, filename):
    #importer.clean_up_database(conn, cur)
    importer.import_raw_data_to_database(conn, filename)
    importer.create_working_data_table(conn, cur)
    importer.create_user_table(conn, cur)
    importer.fill_user_table(conn, cur)
    importer.create_conversations_table(conn, cur)
    importer.create_messages_table(conn, cur)
    importer.create_code_blocks_table(conn, cur)
    print("Database prepared")

def fill_tables(conn, cur):
    #scraper.populate_messages_and_code_block_tables(conn, cur)
    manual_importer.import_manually_split_conversations(conn)
    #importer.create_prompts_table(conn, cur)
    #prompt_parser.parse_prompts(conn, cur) # parses each prompt into conversational, code and other parts
    #prompt_parser.populate_table_retry(conn, cur) # in some cases the system prompt leaked into the results, retrying these
    #prompt_parser.classify_other_again(conn, cur) # some conversational parts were falsely classified as other, retrying these with another system prompt
    #importer.assign_most_used_model_versions(conn, cur)

connection = sqlite3.connect("giicg.db")
cursor = connection.cursor()
#prepare_database(connection, cursor, FILENAME)
fill_tables(connection, cursor)
connection.close()