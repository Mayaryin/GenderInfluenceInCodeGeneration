import importer
import prompt_parser
import scraper
import statistics


def prepare_database():
    importer.create_working_data_table()
    importer.clean_up_database()
    importer.create_user_table()
    importer.create_conversations_table()
    importer.create_messages_table()
    importer.create_code_blocks_table()
    scraper.populate_tables()
    return 0


def main():
    # prepare_database()
    prompt_parser.populate_table()
    statistics.get_user_stats()
    statistics.get_conversation_stats()

if __name__ == '__main__':
    main()