import sqlite3

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field

from helpers.database_client import save_parsed_prompt


def parse_prompts(conn, cursor):
    try:
        cursor.execute("""
                       SELECT message_id, message_text, role
                       FROM prompts
                       WHERE role = 'user';
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} messages to process...")

        for (message_id, message_text, role) in rows:
            try:
                print(f"Processing message {message_id} with id {message_id}")
                result_object = parse_prompt(message_text)
                #Save back to db
                save_parsed_prompt(result_object, message_id, conn)
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.commit()

def populate_table_retry(conn, cursor):
    try:
        # Select all messages where the system prompt leaked into the result during the first run
        cursor.execute("""
                       SELECT messages.message_id, messages.message_text, main.messages.role
                       FROM messages
                       WHERE role = 'user'
                         AND conversational LIKE 'You are tasked with separating%';
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} messages to process...")

        for (message_id, message_text, role,) in rows:
            try:
                print(f"Processing message {message_id} from {role}")
                result_object = parse_prompt(message_text)
                # Save back to db
                save_parsed_prompt(result_object, message_id, conn)
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.commit()


def classify_other_again(conn, cursor):
    try:
        # Select all messages where conversational is empty but other is present
        cursor.execute("""
                       SELECT messages.message_id, messages.other, messages.role
                       FROM messages
                       WHERE role = 'user'
                         AND conversational ='' AND other != '';
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} messages to process...")

        for (message_id, other_message_text, role,) in rows:
            try:
                print(f"Processing message {message_id} from {role}")
                result_object = categorize_text(other_message_text)
                # Save back to db
                if result_object["answer"] == "yes":
                    save_categorized_prompt(other_message_text, message_id, conn)
                print(result_object, other_message_text)
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.commit()


def parse_prompt(prompt_to_analyze):
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    openai_model = "gpt-4o"
    llm = ChatOpenAI(temperature=0.0, model=openai_model)

    class OutputFormat(BaseModel):
        conversational: str = Field(description="The conversational part of the user prompt")
        code: str = Field(description="The code contained in the user prompt")
        other: str = Field(description="Neither code nor conversational part")

    structured_llm = llm.with_structured_output(OutputFormat)

    system_prompt = SystemMessagePromptTemplate.from_template(
        "You are an AI assistant that helps parse prompts."
    )

    user_prompt = HumanMessagePromptTemplate.from_template(
        """You are tasked with separating user prompts into different parts. Prompts may contain of conversational text, code and other parts that are neither conversational nor code. 
                    The prompt is here for you to examine 
                    ---
                    {prompt_to_analyze}
                    ---
                    
                    Some prompts may only contain code, some only conversational text, some only other parts and some of them a mix of components.
                    
                    Output the conversational part, the code and other parts separately. If a component is not present leave that output field blank""",
                        input_variables=["prompt_to_analyze"]
                )

    complete_prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

    chain_one = (
            {"prompt_to_analyze": lambda x: x["prompt_to_analyze"]}
            | complete_prompt
            | structured_llm
            | {"conversational": lambda x: x.conversational,
               "code": lambda x: x.code,
               "other": lambda x: x.other
            }
    )

    return chain_one.invoke({"prompt_to_analyze": prompt_to_analyze})



def categorize_text(text_to_analyze):
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    openai_model = "gpt-4o"
    llm = ChatOpenAI(temperature=0.0, model=openai_model)

    class OutputFormat(BaseModel):
        answer: str = Field(description="Yes or no")

    structured_llm = llm.with_structured_output(OutputFormat)

    system_prompt = SystemMessagePromptTemplate.from_template(
        "You are an AI assistant that helps classify text."
    )

    user_prompt = HumanMessagePromptTemplate.from_template(
        """You are tasked with classifying text snippets. The text might be a human written prompt for a chat bot, a piece of code, an error message or something else that does not fit these categories. 
                    The text is here for you to examine 
                    ---
                    {text_to_analyze}
                    ---

                    Output yes, if the text is likely a human written prompt. Output no, if the text is likely a piece of code, an error message or something else""",
        input_variables=["text_to_analyze"]
    )

    complete_prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

    chain_one = (
            {"text_to_analyze": lambda x: x["text_to_analyze"]}
            | complete_prompt
            | structured_llm
            | {"answer": lambda x: x.answer}
    )

    return chain_one.invoke({"text_to_analyze": text_to_analyze})

def save_categorized_prompt(prompt, message_id, conn):
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE prompts
                   SET conversational = ?
                   WHERE message_id = ?
                   """, (
                       prompt,
                       message_id
                   ))




