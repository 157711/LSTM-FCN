from keras.models import Model
from keras.layers import Input, PReLU, Dense,Dropout, LSTM, Embedding, Conv1D, Flatten, Concatenate, \
                         GlobalMaxPool1D, BatchNormalization

from utils.constants import MAX_NB_WORDS_LIST, MAX_SEQUENCE_LENGTH_LIST, NB_CLASSES_LIST
from utils.keras_utils import train_model, evaluate_model
from utils.embedding_utils import load_embeddings

DATASET_INDEX = 12
OUTPUT_DIM = 1000

MAX_SEQUENCE_LENGTH = MAX_SEQUENCE_LENGTH_LIST[DATASET_INDEX]
MAX_NB_WORDS = MAX_NB_WORDS_LIST[DATASET_INDEX]
NB_CLASS = NB_CLASSES_LIST[DATASET_INDEX]

def generate_model():

    ip = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')

    embedding = Embedding(input_dim=MAX_NB_WORDS, output_dim=OUTPUT_DIM, weights=[load_embeddings('ecg200')],
                          mask_zero=True, input_length=MAX_SEQUENCE_LENGTH, trainable=True)(ip)

    x = LSTM(512, dropout=0.2, recurrent_dropout=0.2)(embedding)

    x = BatchNormalization()(x)

    x = Dense(1024, activation='linear')(x)
    x = PReLU()(x)

    x = Dropout(0.2)(x)

    x = Dense(1024, activation='linear')(x)
    x = PReLU()(x)

    x = Dropout(0.2)(x)

    out = Dense(NB_CLASS, activation='softmax')(x)

    model = Model(ip, out)
    model.summary()

    model.load_weights('./weights/ecg200_weights.h5')

    return model

if __name__ == "__main__":
    model = generate_model()

    train_model(model, DATASET_INDEX, dataset_prefix='ecg200', epochs=101, batch_size=128,
                val_subset=100)

    evaluate_model(model, DATASET_INDEX, dataset_prefix='ecg200', batch_size=128,
                   test_data_subset=100)

