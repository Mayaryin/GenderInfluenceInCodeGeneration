import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from helpers.database_client import insert_code_blocks, insert_message

def populate_messages_and_code_block_tables(connection, cursor):

    # clean tables first
    #cursor.execute("DELETE FROM messages;")
    #cursor.execute("DELETE FROM code_blocks;")
    # Reset the auto-incrementing indices
    #cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages';")
    #cursor.execute("DELETE FROM sqlite_sequence WHERE name='code_blocks';")
    #connection.commit()

    try:
        # Select all non-null and non-empty share_links
        cursor.execute("""
                       SELECT conversations.conversation_id, share_link, user_id
                       FROM conversations
                       WHERE share_link IS NOT NULL
                         AND TRIM(share_link) != '';
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} share links to process...")

        # Iterate and process each share link
        for (conversation_id, share_link, user_id) in rows:
            try:
                print(f"Processing: {share_link}")
                if share_link.startswith("https://claude.ai"):
                    print("scraping claude html file")
                    scrape_from_file("https___claude.ai_share_0dbb90d8-b6cd-4a5d-9d60-c17fc2173321.html", conversation_id, connection)
                else:
                    #continue
                    scrape(share_link, conversation_id, connection)
            except Exception as e:
                print(f"Error processing {share_link}: {e}")

    except Exception as e:
        print(e)
    finally:
        connection.commit()



def scrape(url, conversation_id, connection):
    message_order = 0
    with connection:
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
                    insert_message(
                        connection,
                        conversation_id,
                        role='user',
                        message_text=user_message,
                        message_order=message_order,
                        model_version=None,
                    )
                    message_order += 1

                if llm_reply:
                    message_id = insert_message(
                        connection,
                        conversation_id,
                        role='assistant',
                        message_text=llm_reply,
                        message_order=message_order,
                        model_version=model_version,
                    )
                    if code_blocks:
                     insert_code_blocks(connection, code_blocks, message_id)
                    message_order += 1


def scrape_from_file(html_file_path, conversation_id, connection):
    """
    Parses a pre-downloaded HTML file and inserts data into the database.

    Parameters:
    - html_file_path: str, path to the locally saved HTML file.
    - conversation_id: int, unique ID for the conversation.
    - connection: sqlite3.Connection, database connection.
    """
    if not os.path.isfile(html_file_path):
        print(f"Error: File {html_file_path} does not exist.")
        return

    message_order = 0  # Tracks the order of messages in a conversation
    with connection:
        try:
            # Read the HTML content from the file
            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            # Parse the HTML content
            soup = BeautifulSoup(html_content, "html.parser")

            # Iterate through user and assistant messages
            for index, message_block in enumerate(soup.find_all("div", {"data-test-render-count": "1"})):
                # Extract User Messages
                user_block = message_block.find("div", class_="font-user-message")
                if user_block:
                    user_message = user_block.get_text(strip=True)

                # Extract Assistant Replies
                assistant_block = message_block.find("div", class_="font-claude-message")
                if assistant_block:
                    llm_replies = []
                    code_blocks = []

                    # Collect text content within the assistant block
                    for text_block in assistant_block.find_all(["p", "blockquote"]):
                        text = text_block.get_text(strip=False)
                        if text:
                            llm_replies.append(text)

                    # Collect code blocks within the assistant block
                    for pre in assistant_block.find_all("pre"):
                        # Extract code tokens wrapped with spans
                        code_element = pre.find("code")
                        if code_element:
                            span_tokens = code_element.find_all("span")
                            code_text = "".join(span.get_text(strip=False) for span in span_tokens)

                            # Attempt to determine the language (if available)
                            language = "unknown"
                            if "class" in code_element.attrs:
                                for cls in code_element["class"]:
                                    if cls.startswith("language-"):
                                        language = cls.replace("language-", "")
                                        break

                            if code_text.strip():  # Add code blocks only if text exists
                                code_blocks.append({
                                    "language": language,
                                    "code": code_text.strip(),
                                })

                    llm_reply = "\n\n".join(llm_replies) if llm_replies else None
                    if user_message:
                        insert_message(
                            connection,
                            conversation_id,
                            role='user',
                            message_text=user_message,
                            message_order=message_order,
                            model_version=None,
                        )
                        message_order += 1

                    if llm_reply:
                        message_id = insert_message(
                            connection,
                            conversation_id,
                            role='assistant',
                            message_text=llm_reply,
                            message_order=message_order,
                        )
                        if code_blocks:
                            insert_code_blocks(connection, code_blocks, message_id)
                        message_order += 1

            print("Scraping from file complete!")
        except Exception as e:
            print(f"Error occurred while parsing file {html_file_path}: {e}")


