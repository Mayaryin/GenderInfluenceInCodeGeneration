import sqlite3
import pandas as pd
import tempfile
import subprocess
import os

from statistics import run_t_test_on_gender

pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.width", None)        # Don't wrap lines (use full width)
pd.set_option("display.max_colwidth", None) # Show full content in each cell

conn = sqlite3.connect("giicg.db")

# Filtering out code blocks that are shorter than 5 lines
query = """SELECT 
    cb.code_block_id,
    cb.message_id,
    cb.language,
    cb.code_text,
    m.conversation_id,
    c.user_id,
    u.gender

FROM
    code_blocks cb
JOIN
    messages m ON cb.message_id = m.message_id
JOIN
    conversations c ON m.conversation_id = c.conversation_id
JOIN users u on c.user_id = u.user_id
WHERE
    cb.language = 'python'
    AND (LENGTH(cb.code_text) - LENGTH(REPLACE(cb.code_text, CHAR(10), ''))) > 4
        """

df = pd.read_sql_query(query, conn)
df_female = df[df['gender'] == 'Woman (cisgender)'].sample(n=1, random_state=42)
df_male = df[df['gender'] == 'Man (cisgender)'].sample(n=1, random_state=42)
combined_df = pd.concat([df_female, df_male], ignore_index=True)

def run_pylint_on_code(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ['pylint', '--score=y', '--output-format=text', '--rcfile=.pylintrc', tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout
        errors = result.stderr
        # Extract score from output
        score_line = [line for line in output.split('\n') if 'Your code has been rated at' in line]
        if score_line:
            # Example: "Your code has been rated at 8.00/10"
            score = float(score_line[0].split(' ')[6].split('/')[0])
        else:
            score = None
        # Save the full pylint output and stderr (just in case)
        messages = output.strip() + '\n' + errors.strip()
    finally:
        os.remove(tmp_path)  # Always clean up
    return score, messages

# Apply pylint to each code_text and store scores
def apply_pylint(df):
    scores = []
    messages = []

    for idx, row in df.iterrows():
        print(f"Attempting to run on row {idx}")
        code = row['code_text']
        try:
            score, msg = run_pylint_on_code(code)
        except Exception as e:
            score = None
            msg = f'Error running pylint: {e}'
            print(f"[!] Error with code_block_id {row['code_block_id']}: {e}")

        scores.append(score)
        messages.append(msg)

    df['pylint_score'] = scores
    df['pylint_messages'] = messages
    return df


if __name__ == "__main__":
    print("Running pylint on all code blocks...")
    combined_df = apply_pylint(combined_df)

    print("Average pylint score (Female):", combined_df[combined_df['gender'] == 'Woman (cisgender)']['pylint_score'].mean())
    print("Average pylint score (Male):", combined_df[combined_df['gender'] == 'Man (cisgender)']['pylint_score'].mean())

    # Save to CSV for further offline analysis (optional)
    combined_df.to_csv("code_analysis.csv", index=False)

    # t-test
    run_t_test_on_gender(combined_df, "pylint_score")


