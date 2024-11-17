import nltk
from nltk.corpus import stopwords
import spacy
import numpy as np
import re

nlp = spacy.load("en_core_web_sm")


nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# The function below was created by following the Seq2Seq model tutorial from The Keras Blog


def parse_input_for_model(article, max_sentence_length, num_terms):
    max_sentence_length = 0
    vectorization_mapping = {}
    article_sentences = [[character for character in s.text]
                         for s in nlp(article).sents]
    for sentence in article_sentences:
        max_sentence_length = max(len(sentence), max_sentence_length)
        for character in sentence:
            if character not in vectorization_mapping:
                vectorization_mapping[character] = len(
                    vectorization_mapping)
    article_sentences = article_sentences[3:4]
    print("".join(article_sentences[0]))
    num_sentences = len(article_sentences)
    encoder_input_data = np.zeros(
        (num_sentences, max_sentence_length, num_terms))

    for i, sentence in enumerate(article_sentences):
        for j, character in enumerate(sentence):
            encoder_input_data[i, j, vectorization_mapping[character]] = 1
    print(len(encoder_input_data))
    return encoder_input_data


def parse_input_for_model_new(article, max_sentence_length, num_terms, input_token_index):

    article_sentences = [[character.lower() for character in s.text]
                         for s in nlp(article).sents]
    input_text = article_sentences[1]
    num_encoder_tokens = num_terms
    max_encoder_seq_length = max_sentence_length
    print("".join(input_text))
    encoder_input_data = np.zeros(
        (1, max_encoder_seq_length, num_encoder_tokens),
        dtype="float32",
    )
    print(len(input_text))
    for t, char in enumerate(input_text):
        encoder_input_data[0, t, input_token_index[char]] = 1.0
    encoder_input_data[0, t + 1:, input_token_index[" "]] = 1.0
    return encoder_input_data
