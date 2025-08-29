import spacy

def load_spacy_lanuage_model() -> spacy.language.Language:
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading missing model...")
        spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


################ UNIGRAMS


def get_sec_per_sg_pronouns(text, spacy_model) -> int:
    second_person_pronouns = {"you", "your", "yours", "yourself", "yourselves"}
    doc = spacy_model(text)
    count = 0
    for token in doc:
        if token.lower_ in second_person_pronouns and token.pos_ == "PRON":
            count += 1
    #print("Second person singular pronoun count:", count)
    return count


def get_first_per_pl_pronouns(text, spacy_model) -> int:
    first_plural_pronouns = {"we", "us", "our", "ours", "ourselves"}
    doc = spacy_model(text)
    count = 0
    for token in doc:
        if token.lower_ in first_plural_pronouns and token.pos_ == "PRON":
            count += 1
    #print("First person plural pronoun count:", count)
    return count

def count_please(text: str) -> int:
    # please, pls, plz
    return text.lower().count("please") + text.lower().count("pls") + text.lower().count("plz")

def count_thanks(text: str) -> int:
    return text.lower().count("thanks")

def count_sorry(text: str) -> int:
    return text.lower().count("sorry")

def count_greetings(text: str) -> int:
    # Match only standalone "hi", not "high", "highlight", etc.
    import re
    hi = len(re.findall(r'\bhi\b', text.lower()))
    hello = len(re.findall(r'\bhello\b', text.lower()))
    hey = len(re.findall(r'\bhey\b', text.lower()))
    return hi + hello + hey

def count_help(text: str):
    import re
    return len(re.findall(r'\bhelp\b', text.lower()))


####### BIGRAMS

def count_bigrams(text, spacy_model, n_most_common=10):
    from collections import Counter
    doc = spacy_model(text)
    tokens = [token.lower_ for token in doc if not token.is_punct and not token.is_space]

    bigram_list = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    bigram_counter = Counter(bigram_list)


    #return bigram_counter.most_common(n_most_common)
    return bigram_counter




#def count_would_like(text: str) -> int:
 #   return text.lower().count("would like")

# def count_thank_you(text: str) -> int:
#   return text.lower().count("thank you")

def count_could_you(text: str) -> int:
    return text.lower().count("could you")

def count_can_you(text: str) -> int:
    return text.lower().count("can you")
