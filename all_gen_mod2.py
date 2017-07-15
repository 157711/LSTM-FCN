from keras.models import Model
from keras.layers import Input, PReLU, Dense, LSTM, multiply, concatenate, Activation
from keras.layers import Conv1D, BatchNormalization, GlobalAveragePooling1D, Permute, Dropout

from utils.constants import MAX_SEQUENCE_LENGTH_LIST, NB_CLASSES_LIST
from utils.keras_utils import train_model, evaluate_model, set_trainable, visualise_attention, visualize_cam

ATTENTION_CONCAT_AXIS = 1

def generate_model():
    ip = Input(shape=(1, MAX_SEQUENCE_LENGTH))

    x = LSTM(8)(ip)
    x = Dropout(0.8)(x)

    y = Permute((2, 1))(ip)
    y = Conv1D(128, 8, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = Conv1D(256, 5, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = Conv1D(128, 3, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = GlobalAveragePooling1D()(y)

    x = concatenate([x, y])

    out = Dense(NB_CLASS, activation='softmax')(x)

    model = Model(ip, out)

    cnn_count = 0
    for layer in model.layers:
        if layer.__class__.__name__ in ['Conv1D',
                                        'BatchNormalization',
                                        'PReLU']:
            if layer.__class__.__name__ == 'Conv1D':
                cnn_count += 1

            if cnn_count == 3:
                break
            else:
                set_trainable(layer, TRAINABLE)

    model.summary()

    #model.load_weights("weights/uwave_gesture_library_all_weights - 9606 v3 lstm 128 batch 64 dropout 80 no attention.h5")

    return model


def generate_model_2():
    ip = Input(shape=(1, MAX_SEQUENCE_LENGTH))

    x = attention_block(ip, id=1)
    x = concatenate([ip, x], axis=ATTENTION_CONCAT_AXIS)

    x = LSTM(8)(x)
    x = Dropout(0.8)(x)

    y = Permute((2, 1))(ip)
    y = Conv1D(128, 8, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = Conv1D(256, 5, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = Conv1D(128, 3, padding='same', kernel_initializer='he_uniform')(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)

    y = GlobalAveragePooling1D()(y)

    x = concatenate([x, y])

    out = Dense(NB_CLASS, activation='softmax')(x)

    model = Model(ip, out)

    cnn_count = 0
    for layer in model.layers:
        if layer.__class__.__name__ in ['Conv1D',
                                        'BatchNormalization',
                                        'PReLU']:
            if layer.__class__.__name__ == 'Conv1D':
                cnn_count += 1

            if cnn_count == 3:
                break
            else:
                set_trainable(layer, TRAINABLE)

    #model.summary()

    # add load model code here to fine-tune

    return model


def attention_block(inputs, id):
    # input shape: (batch_size, time_step, input_dim)
    # input shape: (batch_size, max_sequence_length, lstm_output_dim)
    x = Dense(MAX_SEQUENCE_LENGTH, activation='softmax', name='attention_dense_%d' % id)(inputs)
    x = multiply([inputs, x])
    return x


if __name__ == "__main__":

    from keras import backend as K

    dataset_name_prefix = [  # "middle_phalanx_outline_age_group",
        # "middle_phalanx_outline_correct",
        # "middle_phalanx_tw",
        # "plane",
        # "proximal_phalanx_outline_age_group",
        # "ProximalPhalanxOutlineCorrect",
        # "proximal_phalanx_tw",
        # "refrigeration_devices",
        # "screen_type",
        "shapelet_sim",
        "shapes_all",
        "small_kitchen_appliances",
        "sony_aibo",
        "sony_aibo_2",
        "symbols",
        "synthetic_control",
        "toe_segmentation2",
        "wafer",
        "worms",
        "worms_two_class",
        "yoga",
        "mote_strain"]

    idsetnumber = [  # 19,
        # 20,
        # 21,
        # 67,
        # 22,
        # 23,
        # 24,
        # 68,
        # 69,
        70,
        71,
        72,
        17,
        18,
        75,
        76,
        36,
        81,
        82,
        83,
        84,
        25]
    dataset_name_prefix = ["cricket_X"]
    idsetnumber = [30]
    for i in range(0, len(idsetnumber)):
        setting_of_parameters = ""

        global DATASET_INDEX
        DATASET_INDEX = idsetnumber[i]

        global MAX_SEQUENCE_LENGTH
        MAX_SEQUENCE_LENGTH = MAX_SEQUENCE_LENGTH_LIST[DATASET_INDEX]
        global NB_CLASS
        NB_CLASS = NB_CLASSES_LIST[DATASET_INDEX]

        global TRAINABLE
        TRAINABLE = True

        K.clear_session()

        model = generate_model()

        #train_model(model, DATASET_INDEX, dataset_prefix=dataset_name_prefix[i]+setting_of_parameters, epochs=1000, batch_size=32,)

        evaluate_model(model, DATASET_INDEX, dataset_prefix=dataset_name_prefix[i]+setting_of_parameters, batch_size=32)

        visualize_cam(model, DATASET_INDEX, dataset_prefix=dataset_name_prefix[i]+setting_of_parameters, class_id=10)

        #visualise_attention(model, DATASET_INDEX, dataset_prefix=dataset_name_prefix[i]+setting_of_parameters, layer_name='attention_dense_1',
        #                visualize_sequence=True)

