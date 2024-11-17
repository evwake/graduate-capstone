import os
from tensorflow.keras.models import load_model
import numpy as np
import json
from prepare_input_data import parse_input_for_model_new

MODELS = '../../models/'
with open('training_params.json', 'r') as file:
    training_params = json.load(file)

input_token_index = training_params['input_token_index']
target_token_index = training_params['target_token_index']
latent_dim = training_params['latent_dim']
num_encoder_tokens = training_params['num_encoder_tokens']
num_decoder_tokens = training_params['num_decoder_tokens']
max_decoder_seq_length = training_params['max_decoder_seq_length']
max_encoder_seq_length = training_params['max_encoder_seq_length']
encoder_model = load_model('encoder.keras')
decoder_model = load_model('decoder.keras')


test_article_filename = "../../data/Converted Articles/2017-Week 1-Arizona Cardinals-Detroit Lions.txt"
article = ""
with open(test_article_filename, encoding='utf-8') as f:
    for line in f.readlines()[:1]:
        article += line.strip() + " "


input_seq = parse_input_for_model_new(
    article, max_encoder_seq_length, num_encoder_tokens, input_token_index)


reverse_input_char_index = dict((i, char)
                                for char, i in input_token_index.items())
reverse_target_char_index = dict((i, char)
                                 for char, i in target_token_index.items())

# The function below was created by following the Seq2Seq model tutorial from The Keras Blog


def decode_sequence(input_seq):
    states_value = encoder_model.predict(input_seq, verbose=0)

    target_seq = np.zeros((1, 1, num_decoder_tokens))
    target_seq[0, 0, target_token_index["\t"]] = 1.0

    stop_condition = False
    decoded_sentence = ""
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value, verbose=0
        )

        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        if sampled_char == "\n" or len(decoded_sentence) > max_decoder_seq_length:
            stop_condition = True

        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, sampled_token_index] = 1.0

        states_value = [h, c]
    return decoded_sentence


print(decode_sequence(input_seq))
