from helpers.Message import Message

# Only used the prompts from this conversation since conversation is about user code but
# code is not part of the chat since user works with cursor

CONVERSATION_ID = 25
USER_ID = 70
MODEL_VERSION = "Claude 3.7 Sonnet"

message_0 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="Implement d3-force much closer to the way it is in the React version that is added as a comment at the end of the file.",
    model_version="",
    message_order=0,
    conversational="Implement d3-force much closer to the way it is in the React version that is added as a comment at the end of the file.",
    code="",
    other="",
    code_blocks=None
)
message_1 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="Look into collide.js and fix the example",
    model_version="",
    message_order=1,
    conversational="Look into collide.js and fix the example",
    code="",
    other="",
    code_blocks=None
)
message_2 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="It's not working. As soonn as I click \"start force simulation\" all the nodes dissappear.",
    model_version="",
    message_order=2,
    conversational="It's not working. As soonn as I click \"start force simulation\" all the nodes dissappear.",
    code="",
    other="",
    code_blocks=None
)
message_3 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="Cool! Now the only problem is the edges dissappear",
    model_version="",
    message_order=3,
    conversational="Cool! Now the only problem is the edges dissappear",
    code="",
    other="",
    code_blocks=None
)
user_25_convo_70 = [message_0, message_1, message_2, message_3]