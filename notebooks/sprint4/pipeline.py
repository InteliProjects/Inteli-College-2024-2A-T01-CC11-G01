# -*- coding: utf-8 -*-
#!pip install spacy
#!python -m spacy download pt_core_news_sm

import pandas as pd
import spacy
import string
from collections import Counter

nlp = spacy.load("pt_core_news_sm")

def tokenizar(texto):
    """Tokeniza o texto em palavras."""
    doc = nlp(texto)
    return [token.text for token in doc]

def lematizar(tokens):
    """Lemmatiza tokens usando spaCy."""
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]

def remover_stopwords(tokens):
    """Remove stopwords dos tokens."""
    stop_words = set(nlp.Defaults.stop_words)
    return [word for word in tokens if word.lower() not in stop_words]

def remover_pontuacao(tokens):
    """Remove pontuação dos tokens."""
    return [token for token in tokens if token not in string.punctuation]

def pipeline_preprocessamento(frase, intencao, aplicar_tokenizacao=True, aplicar_lematizacao=True,
                              aplicar_remocao_stopwords=True, aplicar_remocao_pontuacao=True):

    output = {'Sentenca Original': frase}

    if aplicar_tokenizacao:
        tokens = tokenizar(frase)

    if aplicar_lematizacao:
        tokens = lematizar(tokens)

    if aplicar_remocao_pontuacao:
        tokens = remover_pontuacao(tokens)

    if aplicar_remocao_stopwords:
        tokens = remover_stopwords(tokens)

    # Contagem de tokens
    sentence_counter = Counter(tokens)

    # Prepare the 'words' information
    words_info = [{'token': token, 'count': sentence_counter[token]} for token in sentence_counter]

    output['words'] = words_info

    # Criar DataFrame
    df_resultado = pd.DataFrame([output])
    return df_resultado

# Exemplo de uso
frase_input = "Qual é a sua intenção com essa pergunta?"
intencao_input = "Consulta"
resultado_df = pipeline_preprocessamento(frase_input, intencao_input)

print(resultado_df)
