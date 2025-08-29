


def compute_personification_score(text: str, spacy_model) -> float:
    tokens = spacy_model(text)
    n_sec_pers_sg = get_sec_per_sg_pronouns(text, spacy_model)
    n_f_pers_pl = get_first_per_pl_pronouns(text, spacy_model)
    n_please = count_please(text)
    #n_thank_you = count_thank_you(text)
    n_thanks = count_thanks(text)
    n_sorry = count_sorry(text)
    #n_could_you = count_could_you(text)
    #n_can_you = count_can_you(text)
    n_greets = count_greetings(text)
    score = ((n_sec_pers_sg + n_f_pers_pl + n_please + n_thanks + n_sorry + n_greets)/len(tokens)) * 100
    return score
