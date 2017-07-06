from keras.models import Model
from keras.layers import Input, PReLU, Dense, Dropout, LSTM, Bidirectional, multiply, concatenate

from utils.constants import MAX_SEQUENCE_LENGTH_LIST, NB_CLASSES_LIST
from utils.keras_utils import train_model, evaluate_model, set_trainable, visualise_attention, visualize_cam

DATASET_INDEX = 36

MAX_SEQUENCE_LENGTH = MAX_SEQUENCE_LENGTH_LIST[DATASET_INDEX]
NB_CLASS = NB_CLASSES_LIST[DATASET_INDEX]

ATTENTION_CONCAT_AXIS = 1  # 1 = temporal, -1 = spatial
TRAINABLE = True


def generate_model():
    ip = Input(shape=(1, MAX_SEQUENCE_LENGTH))

    x = attention_block(ip, id=1)
    x = concatenate([ip, x], axis=ATTENTION_CONCAT_AXIS)

    x = Bidirectional(LSTM(128, trainable=TRAINABLE))(x)

    x = Dense(8192, activation='linear')(x)
    x = PReLU()(x)
    x = Dropout(0.01)(x)

    x = Dense(8192, activation='linear')(x)
    x = PReLU()(x)
    x = Dropout(0.01)(x)

    out = Dense(NB_CLASS, activation='softmax')(x)

    model = Model(ip, out)

    for layer in model.layers[:-4]:
        set_trainable(layer, TRAINABLE)

    model.summary()

    return model


def attention_block(inputs, id):
    # input shape: (batch_size, time_step, input_dim)
    # input shape: (batch_size, max_sequence_length, lstm_output_dim)
    x = Dense(MAX_SEQUENCE_LENGTH, activation='softmax', name='attention_dense_%d' % id)(inputs)
    x = multiply([inputs, x])
    return x


if __name__ == "__main__":
    model = generate_model()

    # train_model(model, DATASET_INDEX, dataset_prefix='toe_segmentation2', epochs=500, batch_size=32)

    evaluate_model(model, DATASET_INDEX, dataset_prefix='toe_segmentation2', batch_size=32)

    visualise_attention(model, DATASET_INDEX, dataset_prefix='toe_segmentation2', layer_name='attention_dense_1')

    visualize_cam(model, DATASET_INDEX, dataset_prefix='toe_segmentation2', class_id=0)
