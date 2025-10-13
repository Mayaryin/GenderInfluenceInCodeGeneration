import spacy
import collections
from collections import Counter
import string

def load_spacy_lanuage_model() -> spacy.language.Language:
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading missing model...")
        spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


########## UNIGRAMS


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


def count_occurrences(text: str, pattern: str, as_word: bool = True) -> int:
    """
    Counts occurrences of a pattern in the text.

    :param text: The text to search within.
    :param pattern: The substring or word to count.
    :param as_word: If True, counts only whole word matches using regex word boundaries.
    :return: The number of occurrences.
    """
    import re
    if as_word:
        regex = r'\b{}\b'.format(re.escape(pattern.lower()))
        return len(re.findall(regex, text.lower()))
    else:
        return text.lower().count(pattern.lower())



def count_punctuation(text):
    standard_punctuation = ".,!?;:'\"()[]\n"
    return Counter(c for c in text if c in standard_punctuation)

def count_newlines(text):
    return text.count("\n")

def divide_counts(counts_dict, total_tokens):
    return Counter({k: v / total_tokens for k, v in counts_dict.items()})


####### BIGRAMS

def count_bigrams(text, spacy_model, n_most_common=10):
    from collections import Counter
    doc = spacy_model(text)
    tokens = [token.lower_ for token in doc if not token.is_punct and not token.is_space]

    bigram_list = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
    bigram_counter = Counter(bigram_list)
    return bigram_counter


def count_would_like(text: str) -> int:
   return text.lower().count("would like")

def count_thank_you(text: str) -> int:
 return text.lower().count("thank you")

def count_could_you(text: str) -> int:
    return text.lower().count("could you")

def count_can_you(text: str) -> int:
    return text.lower().count("can you")

def merge_counts(counts_list):
    import collections
    total_counts = collections.Counter()
    for counts in counts_list:
        total_counts.update(counts)
    return dict(total_counts)
