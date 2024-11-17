import nltk
from nltk.corpus import stopwords
from load_articles import load_articles
import spacy
import numpy as np
import re

nlp = spacy.load("en_core_web_sm")


nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
sentence_pairs = []

articles = load_articles()


def get_sentence_pairs(num_observations):
    global sentence_pairs
    for article_name in articles:
        article = articles.get(article_name)
        recap = article['recap']
        converted = article['converted']
        recap_sentences = [
            [character for character in s.text] for s in nlp(recap).sents]
        converted_sentences = [
            [character for character in s.text] for s in nlp(converted).sents]
        bleu_scores = []
        for recap_sentence in recap_sentences:
            for converted_sentence in converted_sentences:
                BLEUscore = nltk.translate.bleu_score.sentence_bleu(
                    [recap_sentence], converted_sentence)
                bleu_scores.append(
                    (BLEUscore, converted_sentence, recap_sentence))

        for score in bleu_scores:
            if score[0] != 1:
                sentence_pairs.append({"bleu_score": score[0], "converted": "".join(
                    score[1]), "recap": "".join(score[2])})
    sentence_pairs = sorted(
        sentence_pairs, key=lambda x: x["bleu_score"], reverse=True)[:num_observations]

    return sentence_pairs

# The function below was created by following the Seq2Seq model tutorial from The Keras Blog


def get_model_input(num_observations):
    input_texts = []
    target_texts = []
    input_characters = set()
    target_characters = set()
    sentence_pairs = get_sentence_pairs(num_observations)
    for pair in sentence_pairs:
        input_text = pair['converted'].lower()
        target_text = pair['recap'].lower()
        target_text = "\t" + target_text + "\n"
        input_texts.append(input_text)
        target_texts.append(target_text)
        for char in input_text:
            if char not in input_characters:
                input_characters.add(char)
        for char in target_text:
            if char not in target_characters:
                target_characters.add(char)

    input_characters = sorted(list(input_characters))
    target_characters = sorted(list(target_characters))
    num_encoder_tokens = len(input_characters)
    num_decoder_tokens = len(target_characters)
    max_encoder_seq_length = max([len(txt) for txt in input_texts])
    max_decoder_seq_length = max([len(txt) for txt in target_texts])

    print("Number of samples:", len(input_texts))
    print("Number of unique input tokens:", num_encoder_tokens)
    print("Number of unique output tokens:", num_decoder_tokens)
    print("Max sequence length for inputs:", max_encoder_seq_length)
    print("Max sequence length for outputs:", max_decoder_seq_length)

    input_token_index = dict([(char, i)
                             for i, char in enumerate(input_characters)])
    target_token_index = dict([(char, i)
                              for i, char in enumerate(target_characters)])

    encoder_input_data = np.zeros(
        (len(input_texts), max_encoder_seq_length, num_encoder_tokens),
        dtype="float32",
    )
    decoder_input_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens),
        dtype="float32",
    )
    decoder_target_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens),
        dtype="float32",
    )

    for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
        for t, char in enumerate(input_text):
            encoder_input_data[i, t, input_token_index[char]] = 1.0
        encoder_input_data[i, t + 1:, input_token_index[" "]] = 1.0
        for t, char in enumerate(target_text):
            decoder_input_data[i, t, target_token_index[char]] = 1.0
            if t > 0:
                decoder_target_data[i, t - 1, target_token_index[char]] = 1.0
        decoder_input_data[i, t + 1:, target_token_index[" "]] = 1.0
        decoder_target_data[i, t:, target_token_index[" "]] = 1.0
    return encoder_input_data, decoder_input_data, decoder_target_data, num_encoder_tokens, num_decoder_tokens, max_encoder_seq_length, max_decoder_seq_length, input_token_index, target_token_index
