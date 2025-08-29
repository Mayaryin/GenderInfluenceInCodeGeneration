from helpers.Message import Message

# Only used the prompts from this conversation since conversation is about user code but
# code is not part of the chat since user works with cursor

CONVERSATION_ID = 25
USER_ID = 80
MODEL_VERSION = "Claude 3.7 Sonnet"

message_0 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="""
                Implement the built-in components documentation for svelteflow.dev. Orient yourself on the reactflow version.

                Also implement all the example code for every component in apps/example-apps/svelte/guides/built-in-components/. You can take a look how the other 'examples' are implemented for this.

    """,
    model_version="",
    message_order=0,
    conversational="""
                Implement the built-in components documentation for svelteflow.dev. Orient yourself on the reactflow version.

                Also implement all the example code for every component in apps/example-apps/svelte/guides/built-in-components/. You can take a look how the other 'examples' are implemented for this.

    """,
    code="",
    other="",
    code_blocks=None
)

message_1 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="fix the routes fo the remotecodeviewers for svelteflow",
    model_version="",
    message_order=1,
    conversational="fix the routes fo the remotecodeviewers for svelteflow",
    code="",
    other="",
    code_blocks=None
)
message_2 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="make all dependencies.json in the built-in-components example folder simple arrays not objects",
    model_version="",
    message_order=2,
    conversational="make all dependencies.json in the built-in-components example folder simple arrays not objects",
    code="",
    other="",
    code_blocks=None
)
message_3 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="Rework the App.svelte for all the built-in-components example based on the App.svelte from the getting started guide",
    model_version="",
    message_order=3,
    conversational="Rework the App.svelte for all the built-in-components example based on the App.svelte from the getting started guide",
    code="",
    other="",
    code_blocks=None
)

user_25_convo_80 = [message_0, message_1, message_2, message_3]