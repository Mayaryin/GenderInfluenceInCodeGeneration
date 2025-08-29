from typing import Any

from torch import device
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import string
import contractions

def load_spell_correction_model(
        model_name: str = "oliverguhr/spelling-correction-english-base") -> tuple[Any, Any, device]:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print("model loaded")
    return tokenizer, model, device

def correct_spelling(text: str, tokenizer, model, device, max_length: int = 2048) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return text
    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=max_length)
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return corrected

def expand_contractions(text: str) -> str:
    return contractions.fix(text)

def remove_punctuation_and_newlines(text: str) -> str:
    text = text.replace('\n', ' ')
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_newlines(text: str) -> str:
    return text.replace('\n', ' ')

def remove_capitalization(text: str) -> str:
    return text.lower()

def remove_punct_cap(text: str) -> str:
    text = remove_punctuation_and_newlines(text)
    text = remove_capitalization(text)
    return text