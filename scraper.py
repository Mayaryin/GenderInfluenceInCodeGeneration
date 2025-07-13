from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pprint
import sqlite3
import pandas as pd

def populate_tables(db_path="giicg.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Select all non-null and non-empty share_links
        cursor.execute("""
                       SELECT conversations.conversation_id, share_link
                       FROM conversations
                       WHERE share_link IS NOT NULL
                         AND TRIM(share_link) != ''
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} share links to process...")

        # Iterate and process each share link
        for (conversation_id, share_link,) in rows:
            try:
                print(f"Processing: {share_link}")
                scrape_parse_and_save_conversation(share_link, conversation_id, conn)
            except Exception as e:
                print(f"Error processing {share_link}: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.commit()
        conn.close()


def scrape_parse_and_save_conversation(url, conversation_id, conn):
    message_order = 0
    with conn:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            page.wait_for_selector('article[data-testid="conversation-turn-1"]')
            soup = BeautifulSoup(page.content(), 'html.parser')
            parsed = []

            for index, article in enumerate(soup.select('article[data-testid^="conversation-turn-"]')):
                user_block = article.find('div', attrs={'data-message-author-role': 'user'})
                user_message = user_block.get_text(strip=True) if user_block else None

                model_version = None
                assistant_blocks = article.find_all('div', attrs={'data-message-author-role': 'assistant'})
                llm_replies = []
                code_blocks = []

                for assistant in assistant_blocks:
                    if not model_version:
                        model_version = assistant.get("data-message-model-slug", None)

                    text = assistant.get_text(strip=False)
                    if text:
                        llm_replies.append(text)

                    for pre in assistant.find_all("pre"):
                        language_div = pre.find('div', class_='text-xs')
                        language_code = pre.find('code')

                        language = None
                        code_text = None

                        if language_div and language_div.text.strip():
                            language = language_div.text.strip()
                        elif language_code and 'class' in language_code.attrs:
                            for cls in language_code['class']:
                                if cls.startswith("language-"):
                                    language = cls.replace("language-", "")

                        if language_code:
                            code_text = language_code.get_text(strip=False)

                        if code_text:
                            code_blocks.append({
                                'language': language or 'unknown',
                                'code': code_text.strip()
                            })

                llm_reply = "\n\n".join(llm_replies) if llm_replies else None

                if user_message:
                    insert_message_and_code_blocks(
                        conn,
                        conversation_id,
                        role='user',
                        message_text=user_message,
                        message_order=message_order,
                        model_version=None,
                        code_blocks=[]
                    )
                    message_order += 1

                if llm_reply:
                    insert_message_and_code_blocks(
                        conn,
                        conversation_id,
                        role='assistant',
                        message_text=llm_reply,
                        message_order=message_order,
                        model_version=model_version,
                        code_blocks=code_blocks
                    )
                    message_order += 1


def insert_message_and_code_blocks(connection, conversation_id, role, message_text, message_order, model_version=None, code_blocks=None):
    cursor = connection.cursor()
    cursor.execute(
        ''' INSERT INTO messages (
        conversation_id, role, message_text, message_order, model_version) 
            VALUES (?, ?, ?, ?, ?) ''',
        (conversation_id, role, message_text, message_order, model_version)
    )
    message_id = cursor.lastrowid

    if code_blocks:
        for block in code_blocks:
            cursor.execute(
                '''
                INSERT INTO code_blocks (message_id, code_text, language)
                VALUES (?, ?, ?)
            ''',
                (message_id, block['code'], block['language'])
            )

    return message_id


def merge_conversation_turns(parsedArray):
    merged = []
    for index in range(0, len(parsedArray) - 1, 2):
        merged.append({
            'user': parsedArray[index]["user"],
            'assistant': parsedArray[index+1]["assistant"],
            'code_blocks': parsedArray[index+1]["code_blocks"],
            'model_version': parsedArray[index+1]["model_version"],
        })
    return merged


