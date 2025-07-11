import sqlite3
import pandas as pd

def import_to_database(filename):
    df = pd.read_csv(filename)
    print("Columns in CSV:", df.columns)
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()
    df.to_sql("raw_data", connection, if_exists="replace")
    connection.close()


def create_working_data_table():
    connection = sqlite3.connect("giicg.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS working_data")
    cursor.execute('''
        CREATE TABLE main.working_data as
    SELECT "index" as idx,
           "Response ID" as responseId,
           "Last page" as lastpage,
           "Seed" as seed,
           "Please select y.. " as age,
           "What is your hi.. " as education,
           "What is your st.. " as status,
           "What is your fi.. " as study_field,
           "In which year a.. " as study_year,
           "What is your fi.. .1" as work_field,
           "How many years .. " as work_exp_years,
           "In what context..  [At work]" as context_work,
           "In what context..  [At university]" as context_university,
           "In what context..  [Personal projects]" as context_personal,
           "In what context..  [Other]" as context_other,
           "How often do yo.. " as usage_frequency,
           "Is English your.. " as eng_native,
           "How would you d.. " as eng_level,
           "Which of the fo.. " as gender,

           "How do you want.. " as c1_mode,
           "Copy the conver.. " as c1_text,
           "Copy the share .. " as c1_share_link,
           "What LLM versio.. " as c1_llm_version,
           "How would you r.. " as c1_satisfaction,
           "Can you explain.. " as c1_explain_satisfaction,
           "How complex wou.. " as c1_rated_complexity,

           "How do you want.. .1" as c2_mode,
           "Copy the conver.. .1" as c2_text,
           "Copy the share .. .1" as c2_share_link,
           "What LLM versio.. .1" as c2_llm_version,
           "How would you r.. .1" as c2_satisfaction,
           "Can you explain.. .1" as c2_explain_satisfaction,
           "How complex wou.. .1" as c2_rated_complexity,

           "How do you want.. .2" as c3_mode,
           "Copy the conver.. .2" as c3_text,
           "Copy the share .. .2" as c3_share_link,
           "What LLM versio.. .2" as c3_llm_version,
           "How would you r.. .2" as c3_satisfaction,
           "Can you explain.. .2" as c3_explain_satisfaction,
           "How complex wou.. .2" as c3_rated_complexity,

           "How do you want.. .3" as c4_mode,
           "Copy the conver.. .3" as c4_text,
           "Copy the share .. .3" as c4_share_link,
           "What LLM versio.. .3" as c4_llm_version,
           "How would you r.. .3" as c4_satisfaction,
           "Can you explain.. .3" as c4_explain_satisfaction,
           "How complex wou.. .3" as c4_rated_complexity,

           "How do you want.. .4" as c5_mode,
           "Copy the conver.. .4" as c5_text,
           "Copy the share .. .4" as c5_share_link,
           "What LLM versio.. .4" as c5_llm_version,
           "How would you r.. .4" as c5_satisfaction,
           "Can you explain.. .4" as c5_explain_satisfaction,
           "How complex wou.. .4" as c5_rated_complexity,

           "LLMs are helpfu.. " as llms_helpful,
           "I enjoy using L.. " as llms_enjoy,
           "I would like to.. " as llms_go_back,
           "I have become f.. " as llms_faster,
           "I have become s.. " as llms_slower,
           "I am employing .. " as llms_prompt_enigneering,
           "My way to appro.. " as llms_approach,
           "Can you describ.. " as llms_describe_approach,
           "I have ethical .. " as llms_ethical_concerns,
           "Can you specify..  [LLMs can reprod.. ]" as llms_ec_bias,
           "Can you specify..  [LLMs can reprod.. ].1" as llms_ec_discrimination,
           "Can you specify..  [LLMs can lead t.. ]" as llms_ec_skill_loss,
           "Can you specify..  [LLM users can l.. ]" as llms_ec_learn_less,
           "Can you specify..  [LLMs can lead t.. ].1" as llms_ec_diversity_loss,
           "Can you specify..  [Other:]" as llms_ec_other,
           "What other conc.. " as llms_other_concerns,
           "Do you have any.. " as llms_other_toughts

from raw_data;
    ''')




