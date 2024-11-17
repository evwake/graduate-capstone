from keras.models import Model
from keras.layers import Input, LSTM, Dense
from keras.callbacks import EarlyStopping
from get_input_and_output import get_model_input
import tensorflow as tf
import json
import os


physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


MODELS_FOLDER = '../Models/'

num_observations = 10000
encoder_input_data, decoder_input_data, decoder_target_data, num_encoder_tokens, num_decoder_tokens, max_encoder_seq_length, max_decoder_seq_length, input_token_index, target_token_index = get_model_input(
    num_observations)
latent_dim = 128
batch_size = 64
epochs = 100

# The model training below was created by following the Seq2Seq model tutorial from The Keras Blog

encoder_inputs = Input(shape=(None, num_encoder_tokens))
encoder = LSTM(latent_dim, return_state=True,
               dropout=0.3, recurrent_dropout=0.3)
encoder_outputs, state_h, state_c = encoder(encoder_inputs)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(None, num_decoder_tokens))

decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                     initial_state=encoder_states)
decoder_dense = Dense(num_decoder_tokens, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy', metrics=['accuracy'])


stopping_func = EarlyStopping(
    monitor="val_loss", min_delta=0.0005, patience=15, verbose=1, restore_best_weights=True)

training_info = model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
                          batch_size=batch_size,
                          epochs=epochs,
                          validation_split=0.2,
                          callbacks=[stopping_func])

model.save('model.keras')

folder_path = f'{MODELS_FOLDER}{num_observations}_observations_{epochs}_epochs_{batch_size}_batch_size_{latent_dim}_latent_dim/'
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

training_loss = training_info.history['loss']
training_val_loss = training_info.history['val_loss']

with open(folder_path + 'training_loss.json', 'w') as f:
    json.dump(training_loss, f)

with open(folder_path + 'training_val_loss.json', 'w') as f:
    json.dump(training_val_loss, f)


encoder_model = Model(encoder_inputs, encoder_states)

decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_outputs, state_h, state_c = decoder_lstm(
    decoder_inputs, initial_state=decoder_states_inputs)
decoder_states = [state_h, state_c]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs] + decoder_states)


encoder_model.save(folder_path + 'encoder.keras')
decoder_model.save(folder_path + 'decoder.keras')

training_params = dict()

training_params['latent_dim'] = latent_dim
training_params['num_encoder_tokens'] = num_encoder_tokens
training_params['num_decoder_tokens'] = num_decoder_tokens
training_params['max_encoder_seq_length'] = max_encoder_seq_length
training_params['max_decoder_seq_length'] = max_decoder_seq_length
training_params['input_token_index'] = input_token_index
training_params['target_token_index'] = target_token_index
with open(folder_path + '/training_params.json', 'w') as f:
    json.dump(training_params, f)
