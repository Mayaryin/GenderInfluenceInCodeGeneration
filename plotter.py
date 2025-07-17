import sqlite3

import pandas as pd

import matplotlib.pyplot as plt

from statistics import make_average_convo_length_query, make_llm_version_query, make_code_blocks_with_convo_id_query

plt.style.use('ggplot')

conn = sqlite3.connect('giicg.db')
user_df = pd.read_sql_query("SELECT * FROM users WHERE lastpage > 2", conn)

ax = user_df["gender"].value_counts().sort_values().plot(kind="bar", title="Gender Distribution", figsize=(12, 8))
ax.set_xlabel("Gender")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_helpful"].value_counts().sort_values().plot(kind="bar", title="LLMs are helpful for writing code", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_enjoy"].value_counts().sort_values().plot(kind="bar", title="I enjoy using LLMs in my work or for studying.", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_go_back"].value_counts().sort_values().plot(kind="bar", title=" I would like to go back to the time before they existed", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_faster"].value_counts().sort_values().plot(kind="bar", title="I have become faster at learning new programming skills through using LLMs", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_slower"].value_counts().sort_values().plot(kind="bar", title=" I have become slower at learning new programming skills through using LLMs", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_prompt_enigneering"].value_counts().sort_values().plot(kind="bar", title="I am employing specific prompting techniques when prompting LLMs", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_approach"].value_counts().sort_values().plot(kind="bar", title="My way to approach new programming challenges has changed through using LLMs.", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["llms_ethical_concerns"].value_counts().sort_values().plot(kind="bar", title="I have ethical concerns about the technology.", figsize=(12, 8))
ax.set_xlabel("Response")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


all_users_df = pd.read_sql_query("SELECT * FROM users", conn)

ax = all_users_df["usage_frequency"].value_counts().sort_values().plot(kind="bar", title="Usage Frequency (all participants)", figsize=(12, 8))
ax.set_xlabel("Usage")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

ax = user_df["age"].value_counts().sort_index().plot(kind="bar", title="Age Distribution", figsize=(12, 8))
ax.set_xlabel("Age")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

query = make_average_convo_length_query()
message_count_df = pd.read_sql_query(query, conn)

ax = message_count_df.sort_values('gender')['avg_messages_per_convo_per_gender'].plot( kind="bar", title="Average Message Count per User by Gender", figsize=(12, 8) )
ax.set_xlabel("Gender")
ax.set_ylabel("Average Message Count")
ax.set_xticks(range(len(message_count_df)))
ax.set_xticklabels(message_count_df.sort_values("gender")["gender"], rotation=45, ha="right")
plt.tight_layout()
plt.show()


llm_version_df = pd.read_sql_query("""SELECT * FROM conversation_model_version """, conn)

ax = llm_version_df["assigned_model_version"].value_counts().sort_index().plot(kind="bar", title="Model versions", figsize=(12, 8))
ax.set_xlabel("Model Version")
ax.set_ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


query = make_code_blocks_with_convo_id_query()
language_df = pd.read_sql_query(query, conn)

ax = language_df["language"].value_counts().sort_index().plot(kind="bar", title="Programming Languages", figsize=(12, 8))
ax.set_xlabel("Programming Languages")
ax.set_ylabel("Number of Code Blocks")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()





