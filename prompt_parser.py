import sqlite3

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field

def populate_table(db_path="giicg.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Select all messages with role = user
        cursor.execute("""
                       SELECT messages.message_id, messages.message_text, main.messages.role
                       FROM messages
                       WHERE role = 'user' 
                       """)
        rows = cursor.fetchall()

        print(f"Found {len(rows)} messages to process...")

        # Iterate and process each message
        for (message_id, message_text, role,) in rows:
            try:
                print(f"Processing message {message_id} from {role}")
                result_object = parse_prompt(message_text)
                #Save back to db
                save_parsed_prompt(result_object, message_id, conn)
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")

    except Exception as e:
        print(e)
    finally:
        conn.commit()
        conn.close()


def parse_prompt(prompt_to_analyze):
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    openai_model = "gpt-4o-mini"
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

def save_parsed_prompt(result_object, message_id, conn):
    cursor = conn.cursor()
    #cursor.execute("ALTER TABLE messages ADD COLUMN conversational TEXT;")
    #cursor.execute("ALTER TABLE messages ADD COLUMN code TEXT;")
    #cursor.execute("ALTER TABLE messages ADD COLUMN other TEXT;")

    cursor.execute("""
                   UPDATE messages
                   SET conversational = ?,
                       code           = ?,
                       other          = ?
                   WHERE message_id = ?
                   """, (
                       result_object["conversational"],
                       result_object["code"],
                       result_object["other"],
                       message_id
                   ))



