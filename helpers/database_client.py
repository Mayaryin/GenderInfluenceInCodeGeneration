def insert_message(connection, conversation_id, role, message_text, message_order, model_version=None):
    cursor = connection.cursor()
    cursor.execute(
        ''' INSERT INTO messages (
        conversation_id, role, message_text, message_order, model_version) 
            VALUES (?, ?, ?, ?, ?) ''',
        (conversation_id, role, message_text, message_order, model_version)
    )
    message_id = cursor.lastrowid
    return message_id

def insert_code_blocks(connection, code_blocks, message_id):
    cursor = connection.cursor()
    for block in code_blocks:
        cursor.execute(
            '''
            INSERT INTO code_blocks (message_id, code_text, language)
            VALUES (?, ?, ?)
            ''',
            (message_id, block['code'], block['language'])
        )
    prompt_id = cursor.lastrowid
    return prompt_id

def insert_prompt(connection, conversation_id, role, message_text, conversational=None, code=None, other=None):
    cursor = connection.cursor()
    cursor.execute(
        ''' INSERT INTO prompts (
        conversation_id, role, message_text, conversational, code, other) 
            VALUES (?, ?, ?, ?, ?, ?) ''',
        (conversation_id, role, message_text,conversational, code, other)
    )
    prompt_id = cursor.lastrowid
    return prompt_id

def save_parsed_prompt(result_object, message_id, conn):
    cursor = conn.cursor()

    cursor.execute("""
                   UPDATE prompts
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