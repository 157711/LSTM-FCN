from keras.models import Model
from keras.layers import Input, PReLU, Dense,Dropout, LSTM, Embedding, BatchNormalization

from utils.constants import MAX_NB_WORDS_LIST, MAX_SEQUENCE_LENGTH_LIST, NB_CLASSES_LIST
from utils.keras_utils import train_model, evaluate_model

DATASET_INDEX = 18
OUTPUT_DIM = 2000

MAX_SEQUENCE_LENGTH = MAX_SEQUENCE_LENGTH_LIST[DATASET_INDEX]
MAX_NB_WORDS = MAX_NB_WORDS_LIST[DATASET_INDEX]
NB_CLASS = NB_CLASSES_LIST[DATASET_INDEX]

def generate_model():

    ip = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')

    embedding = Embedding(input_dim=MAX_NB_WORDS, output_dim=OUTPUT_DIM,
                          mask_zero=True, input_length=MAX_SEQUENCE_LENGTH)(ip)

    x = LSTM(1024, dropout=0.2, recurrent_dropout=0.2)(embedding)

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

    return model

if __name__ == "__main__":
    model = generate_model()

    # use Large model here (2000 embedding space, 1024 LSTM cells)

    #train_model(model, DATASET_INDEX, dataset_prefix='sony_aibo_2', epochs=50, batch_size=16,
    #            val_subset=953)

    evaluate_model(model, DATASET_INDEX, dataset_prefix='sony_aibo_2', batch_size=128,
                test_data_subset=953)

