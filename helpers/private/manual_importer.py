from helpers.scraper import insert_message, insert_code_blocks
from helpers.private.user_25_convo_70 import user_25_convo_70
from helpers.private.user_25_convo_80 import user_25_convo_80
from helpers.private.user_29_convo_37 import user_29_convo_37
from helpers.private.user_15_convo_5 import user_5_convo_15
from helpers.private.user_63_convo_19 import user_63_convo_19
from helpers.private.user_83_convo_25 import user_83_convo_25
from helpers.private.user_8_convo_2 import user_8_convo_2


def import_manually_split_conversations(connection):

    messages = []
    #messages.extend(user_5_convo_15)
    #messages.extend(user_25_convo_70)
    #messages.extend(user_83_convo_25)
    messages.extend(user_29_convo_37)
    #messages.extend(user_63_convo_19)
    #messages.extend(user_25_convo_80)
    messages.extend(user_8_convo_2)

    with connection:

        for message in messages:
            try:
                print("inserting message: ", message.message_text, " ...")
                message_id = insert_message(
                    connection,
                    message.conversation_id,
                    role=message.role,
                    message_text=message.message_text,
                    message_order=message.message_order,
                    model_version=message.model_version,
                    conversational=message.conversational,
                    code=message.code,
                    other=message.other,
                )
                if message.code_blocks:
                    print("inserting code blocks: ", message.code_blocks[0], " ...")
                    insert_code_blocks(connection, message.code_blocks, message_id)

            except Exception as e:
                print(f"Error inserting message {message.message_text}: {e}")