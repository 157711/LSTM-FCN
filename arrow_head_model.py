from keras.models import Model
from keras.layers import Input, PReLU, Dense,Dropout, LSTM, Embedding, Bidirectional
from phased_lstm_keras.PhasedLSTM import PhasedLSTM

from utils.constants import MAX_NB_WORDS_LIST, MAX_SEQUENCE_LENGTH_LIST, NB_CLASSES_LIST
from utils.keras_utils import train_model, evaluate_model, set_trainable

DATASET_INDEX = 1
OUTPUT_DIM = 300
TRAINABLE = True

MAX_SEQUENCE_LENGTH = MAX_SEQUENCE_LENGTH_LIST[DATASET_INDEX]
MAX_NB_WORDS = MAX_NB_WORDS_LIST[DATASET_INDEX]
NB_CLASS = NB_CLASSES_LIST[DATASET_INDEX]

def generate_model():

    ip = Input(shape=(MAX_SEQUENCE_LENGTH,), dtype='int32')

    embedding = Embedding(input_dim=MAX_NB_WORDS, output_dim=OUTPUT_DIM,
                          mask_zero=True, input_length=MAX_SEQUENCE_LENGTH)(ip)

    #x = Bidirectional(LSTM(256, dropout=0.2, recurrent_dropout=0.2, trainable=TRAINABLE))(embedding)
    x = PhasedLSTM(128)(embedding)

    x = Dense(1024, activation='linear')(x)
    x = PReLU()(x)

    x = Dropout(0.2)(x)

    x = Dense(1024, activation='linear')(x)
    x = PReLU()(x)

    x = Dropout(0.2)(x)

    out = Dense(NB_CLASS, activation='softmax')(x)

    model = Model(ip, out)

    for layer in model.layers[:-4]:
        set_trainable(layer, TRAINABLE)

    model.summary()

    #model.load_weights('weights/arrow_head_weights - 8457.h5')

    return model


if __name__ == "__main__":
    model = generate_model()

    train_model(model, DATASET_INDEX, dataset_prefix='arrow_head', epochs=100, batch_size=128,
                val_subset=175)

    evaluate_model(model, DATASET_INDEX, dataset_prefix='arrow_head', batch_size=128,
                  test_data_subset=175)


