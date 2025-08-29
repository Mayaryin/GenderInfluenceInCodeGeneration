from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
import torch


def load_language_detection_model():
    model_ckpt = "papluca/xlm-roberta-base-language-detection"
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(model_ckpt)
    return tokenizer, model

def detect_language(text: str, tokenizer, model) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return "unknown"
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=-1)
    pred_idx = torch.argmax(probs, dim=1).item()  # Get index of highest probability
    # confidence = probs[0][pred_idx].item()

    # Map index to label
    id2lang = model.config.id2label
    language = id2lang[pred_idx]

    return language



def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

def translate(text, tokenizer, model):
    input_ids = tokenizer.encode(text, return_tensors="pt", add_special_tokens=True)
    output_ids = model.generate(input_ids)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

def conditional_translation(row, de_tokenizer, de_model, it_tokenizer, it_model, column):
    if row['language'] == 'de':
        return translate(row[column], de_tokenizer, de_model)
    if row['language'] == 'it':
        return translate(row[column], it_tokenizer, it_model)
    return row[column]