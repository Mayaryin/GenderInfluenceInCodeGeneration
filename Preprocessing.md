# Processing Pipeline


## Raw data
- Raw data is imported into table raw_data
- all colums are renamed to shorter handles 
- schema is created:
  - table users containing only user information
  - table conversations containing user id and conversation information
  - table messages containing message_id, conversation_id, role, message_text, conversational, code, other
  - table code_blocks containing code_block_id, message_id, code_text and language
  - table prompts containing the message_id, conversation_id, role, message_text, gender and user_id for all messages with role user. this table will be altered in the following steps and it will be the central working table for prompt analysis

## Preprocessing
- messages and code_blocks table are filled by a scraper module that scrapes all share links and parses them into user and assistant message as well as code blocks from the assitant replies
- a manual parsing process adds all conversations which were provided as raw text to the messages and code blocks table
- the prompts table is extended by colummns 'conversational', 'code' and 'other' by a parsing module that separates each prompt into its parts
- the prompt parser is retried on rows where the system prompt leaked into the output

## Normalization
- all prompts are annotated by their language 
- all prompts that are not english are translated to english, the results overwrite the conversational column in the prompts table

## Problems
- the prompt parsing model has difficulties detecting the right category especially for italian, which leads to some conversational context being classified as other and will be missing fom the analyses
- in some cases the system prompt leaked into the results, these are retried, but in every run only 2-3 more rows are categorized. Either these lines have to be processed manually or will be excluded. Right now this concerns 41 of 878 rows, so approx 5%
- running the pipeline again might change results since the outputs of models used for normalization are not deterministic
- max 142 prompts do not have a conversational part, some of that is worngly classified, these will be excluded from the analyses or manually selcted or retried with another system prompt