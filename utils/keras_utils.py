import os
import numpy as np

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV

import warnings
warnings.simplefilter('ignore', category=DeprecationWarning)

from keras.models import Model
from keras.layers import Permute
from keras.optimizers import Adam
from keras.utils import to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.wrappers.scikit_learn import KerasClassifier
from keras import backend as K

from utils.generic_utils import load_dataset_at, calculate_dataset_metrics
from utils.constants import MAX_SEQUENCE_LENGTH_LIST


def train_model(model:Model, dataset_id, dataset_prefix, epochs=50, batch_size=128, val_subset=None):

    X_train, y_train, X_test, y_test, is_timeseries = load_dataset_at(dataset_id)
    max_nb_words, sequence_length = calculate_dataset_metrics(X_train)

    if sequence_length != MAX_SEQUENCE_LENGTH_LIST[dataset_id]:
        print("Original sequence length was :", sequence_length, "New sequence Length will be : ", MAX_SEQUENCE_LENGTH_LIST[dataset_id])
        input('Press enter to acknowledge this and continue : ')

    if not is_timeseries:
        X_train = pad_sequences(X_train, maxlen=MAX_SEQUENCE_LENGTH_LIST[dataset_id], padding='post', truncating='post')
        X_test = pad_sequences(X_test, maxlen=MAX_SEQUENCE_LENGTH_LIST[dataset_id], padding='post', truncating='post')

    classes = np.unique(y_train)
    le = LabelEncoder()
    y_ind = le.fit_transform(y_train.ravel())
    recip_freq = len(y_train) / (len(le.classes_) *
                           np.bincount(y_ind).astype(np.float64))
    class_weight = recip_freq[le.transform(classes)]

    print("Class weights : ", class_weight)

    y_train = to_categorical(y_train, len(np.unique(y_train)))
    y_test = to_categorical(y_test, len(np.unique(y_test)))

    model_checkpoint = ModelCheckpoint("./weights/%s_weights.h5" % dataset_prefix, verbose=1,
                                       monitor='val_acc', save_best_only=True, save_weights_only=True)
    reduce_lr = ReduceLROnPlateau(monitor='val_acc', patience=5, mode='max',
                                  factor=0.70710678118, cooldown=5, min_lr=1e-6, verbose=2) # cube root of 2
    callback_list = [model_checkpoint, reduce_lr]

    optm = Adam(lr=1e-3)

    model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    if val_subset is not None:
        X_test = X_test[:val_subset]
        y_test = y_test[:val_subset]

    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, callbacks=callback_list,
              class_weight=class_weight, verbose=1, validation_data=(X_test, y_test))


def evaluate_model(model:Model, dataset_id, dataset_prefix, batch_size=128, test_data_subset=None):
    X_train, y_train, X_test, y_test, is_timeseries = load_dataset_at(dataset_id)

    if not is_timeseries:
        X_test = pad_sequences(X_test, maxlen=MAX_SEQUENCE_LENGTH_LIST[dataset_id], padding='post', truncating='post')
    y_test = to_categorical(y_test, len(np.unique(y_test)))

    optm = Adam(lr=1e-3)
    model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

    model.load_weights("./weights/%s_weights.h5" % dataset_prefix)

    if test_data_subset is not None:
        X_test = X_test[:test_data_subset]
        y_test = y_test[:test_data_subset]

    print("\nEvaluating : ")
    loss, accuracy = model.evaluate(X_test, y_test, batch_size=batch_size)
    print()
    print("Final Accuracy : ", accuracy)


def hyperparameter_search_over_model(model_gen, dataset_id, param_grid):

    X_train, y_train, _, _, is_timeseries = load_dataset_at(dataset_id)
    if not is_timeseries:
        print("Model hyper parameters can only be searched for time series models")
        return

    classes = np.unique(y_train)
    le = LabelEncoder()
    y_ind = le.fit_transform(y_train.ravel())
    recip_freq = len(y_train) / (len(le.classes_) *
                                 np.bincount(y_ind).astype(np.float64))
    class_weight = recip_freq[le.transform(classes)]

    y_train = to_categorical(y_train, len(np.unique(y_train)))

    clf = KerasClassifier(build_fn=model_gen,
                          epochs=50,
                          class_weight=class_weight,
                          verbose=0)

    grid = GridSearchCV(clf, param_grid=param_grid,
                        n_jobs=1, verbose=10, cv=3)

    result = grid.fit(X_train, y_train)

    print("Best: %f using %s" % (result.best_score_, result.best_params_))
    means = result.cv_results_['mean_test_score']
    stds = result.cv_results_['std_test_score']
    params = result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print("%f (%f) with: %r" % (mean, stdev, param))


def set_trainable(layer, value):
   layer.trainable = value

   # case: container
   if hasattr(layer, 'layers'):
       for l in layer.layers:
           set_trainable(l, value)

   # case: wrapper (which is a case not covered by the PR)
   if hasattr(layer, 'layer'):
        set_trainable(layer.layer, value)


def build_function(model, layer_name=None):
    inp = model.input
    if layer_name is None:
        outputs = [layer.output for layer in model.layers] # all layer outputs
    else:
        outputs = [layer.output for layer in model.layers if layer.name == layer_name]

    funcs = [K.function([inp] + [K.learning_phase()], [out]) for out in outputs]  # evaluation functions
    return funcs


def get_activations(model, inputs, eval_functions, layer_name=None):
    # Documentation is available online on Github at the address below.
    # From: https://github.com/philipperemy/keras-attention-mechanism/blob/master/attention_utils.py
    # From: https://github.com/philipperemy/keras-visualize-activations
    print('----- activations -----')
    activations = []
    layer_outputs = [func([inputs, 1.])[0] for func in eval_functions]
    for layer_activations in layer_outputs:
        activations.append(layer_activations)
    return activations


def visualise_attention(model:Model, dataset_index, dataset_prefix, layer_name, print_attention=False):
    _, _, X_test, _, is_timeseries = load_dataset_at(dataset_index)

    model.load_weights("./weights/%s_weights.h5" % dataset_prefix)

    eval_functions = build_function(model, layer_name)
    attention_vectors = []

    for i in range(X_test.shape[0]):
        print(X_test[i, :, :][np.newaxis, ...].shape)
        attention_vector = np.mean(get_activations(model,
                                                   X_test[i, :, :][np.newaxis, ...],
                                                   eval_functions,
                                                   layer_name=layer_name)[0], axis=1).squeeze()

        if print_attention: print('attention =', attention_vector)
        assert (np.sum(attention_vector) - 1.0) < 1e-5
        attention_vectors.append(attention_vector)

    attention_vectors = np.array(attention_vectors)
    print(attention_vectors.shape)
    attention_vector_final = np.mean(attention_vectors, axis=0)

    # plot part.
    import matplotlib.pyplot as plt
    import pandas as pd

    df = pd.DataFrame({'attention (%)': attention_vector_final},
                      index=range(attention_vector_final.shape[0]))

    df['attention (%)'].plot(kind='bar',
            title='Attention Mechanism as '
            'a function of input'
            ' dimensions.')
    plt.show()


class MaskablePermute(Permute):

    def __init__(self, dims, **kwargs):
        super(MaskablePermute, self).__init__(dims, **kwargs)
        self.supports_masking = True
