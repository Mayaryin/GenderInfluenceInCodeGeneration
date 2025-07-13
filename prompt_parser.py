from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field

def parse_prompts(prompt):
    load_dotenv()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    openai_model = "gpt-4o-mini"
    llm = ChatOpenAI(temperature=0.0, model=openai_model)

    class OutputFormat(BaseModel):
        conversational_text: str = Field(description="The conversational part of the user prompt")
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

    print(complete_prompt.format(prompt_to_analyze="TEST STRING"))

    chain_one = (
            {"prompt_to_analyze": lambda x: x["prompt_to_analyze"]}
            | complete_prompt
            | structured_llm
            | {"conversational_text": lambda x: x.conversational_text,
               "code": lambda x: x.code,
               "other": lambda x: x.other
            }
    )

    return chain_one.invoke({"prompt_to_analyze": prompt_to_analyze})




prompt_to_analyze = """"import os
import pandas as pd
import numpy as np


# Paths to directories
data_dir = "/home/helena/Documents/bachelors_thesis/MMIST-ccRCC/data/data_files"
ct_dir = os.path.join(data_dir, "features", "CT_features")
mri_dir = os.path.join(data_dir, "features", "MRI_features")
wsi_dir = os.path.join(data_dir, "features", "WSI_features")
clinical_file = os.path.join(data_dir, "clinical+genomic_split.csv")

# Import lists of chosen samples
ct_chosen_samples = pd.read_csv(os.path.join(data_dir, "selected_using_MIL", "CT_ammended.csv"))
mri_chosen_samples = pd.read_csv(os.path.join(data_dir, "selected_using_MIL", "MRI_ammended.csv"))
wsi_chosen_samples = pd.read_csv(os.path.join(data_dir, "selected_using_MIL", "WSI_patientfiles.csv"))

# Storage for extracted features
data = {
    "CT": {},
    "MRI": {},
    "WSI": {},
    "clinical": None
}

def load_npz_files(chosen_samples, feature_dir, modality):
    for _, row in chosen_samples.iterrows():
        file_identifier = row['chosen_exam']
        key = row['case_id']
        feature_path = os.path.join(feature_dir, file_identifier)
        
        # Load the file if it exists
        if os.path.exists(feature_path):
            data[modality][key] = np.load(feature_path)
        else:
            print(f"Warning: {file_identifier} not found for {modality}.")

load_npz_files(ct_chosen_samples, ct_dir, "CT")
load_npz_files(mri_chosen_samples, mri_dir, "MRI")
load_npz_files(wsi_chosen_samples, wsi_dir, "WSI")

# Load clinical data and restrict to chosen cases
clinical_data = pd.read_csv(clinical_file)
clinical_data = clinical_data.set_index('case_id')

clinical_data.fillna(0, inplace=True)
# Convert all columns (except 'Split') to numeric
for col in clinical_data.columns:
    if col != 'Split':
        clinical_data[col] = pd.to_numeric(clinical_data[col], errors='coerce')
clinical_data.fillna(0, inplace=True)
data["clinical"] = clinical_data

print("Number of CT feature files:", len(data["CT"]))
print("Number of MRI feature files:", len(data["MRI"]))
print("Number of WSI feature files:", len(data["WSI"]))

if data["clinical"] is not None:
    print("Number of clinical records:", len(data["clinical"]))
else:
    print("Clinical data not loaded.")


# Determine train/test splits (assumes 'Split' column in clinical data)
clinical_full = pd.read_csv(clinical_file)
train_ids = clinical_full[clinical_full['Split'] == 'train']['case_id'].tolist()
test_ids = clinical_full[clinical_full['Split'] == 'test']['case_id'].tolist()

def map_features_by_ids(features_dict, ids_list):
    mapped_features = {}
    for case_id in ids_list:
        if case_id in features_dict:
            mapped_features[case_id] = features_dict[case_id]
    return mapped_features

# # Inspect a few samples from each modality
# for modality in ["CT", "MRI", "WSI"]:
#     print(f"\n--- {modality} Samples ---")
#     count = 0
#     for key, npz_file in data[modality].items():
#         sample_arr = npz_file['arr_0']
#         print(f"Case ID: {key}")
#         print(f"Shape: {sample_arr.shape}")
#         print(f"First few values: {sample_arr.flatten()[:5]}\n")
#         count += 1
#         if count >= 30:  # just inspect 3 samples per modality
#             break

maybe this file will help you write this code correctly"""

print(parse_prompts(prompt_to_analyze))
