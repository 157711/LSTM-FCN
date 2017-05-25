import numpy as np
import pandas as pd

from utils.constants import TRAIN_FILES, TEST_FILES

def load_dataset_at(index) -> (np.array, np.array):
    assert index < len(TRAIN_FILES), "Index invalid. Could not load dataset at %d" % index
    print("Loading train / test dataset : ", TRAIN_FILES[index], TEST_FILES[index])

    df = pd.read_csv(TRAIN_FILES[index], header=None, encoding='latin-1')

    # remove all columns which are completely empty
    df.dropna(axis=1, how='all', inplace=True)

    # fill all missing columns with 0
    df.fillna(0, inplace=True)

    # cast all data into integer (int32)
    df[df.columns] = df[df.columns].astype(np.int32)

    # extract labels Y and normalize to [0 - (MAX - 1)] range
    labels = df[[0]]
    labels = labels - labels.min()

    # drop labels column from train set X
    df.drop(df.columns[0], axis=1, inplace=True)

    X_train = df.values
    y_train = labels.values

    print("Finished loading train dataset..")

    df = pd.read_csv(TEST_FILES[index], header=None, encoding='latin-1')

    # remove all columns which are completely empty
    df.dropna(axis=1, how='all', inplace=True)

    # fill all missing columns with 0
    df.fillna(0, inplace=True)

    # cast all data into integer (int32)
    df[df.columns] = df[df.columns].astype(np.int32)

    # extract labels Y and normalize to [0 - (MAX - 1)] range
    labels = df[[0]]
    labels = labels - labels.min()

    # drop labels column from train set X
    df.drop(df.columns[0], axis=1, inplace=True)

    X_test = df.values
    y_test = labels.values

    print("Finished loading test dataset..")

    return X_train, y_train, X_test, y_test


def calculate_dataset_metrics(X_train):
    max_sequence_length = X_train.shape[-1]
    max_nb_words = np.amax(X_train)

    return max_nb_words, max_sequence_length


if __name__ == "__main__":
    word_list = []
    seq_len_list = []
    classes = []

    for index in range(17):
        x, y, x_test, y_test = load_dataset_at(index)
        nb_words, seq_len = calculate_dataset_metrics(x)
        print("-" * 80)
        print("Dataset : ", index + 1)
        print("Train :: X shape : ", x.shape, "Y shape : ", y.shape, "Nb classes : ", len(np.unique(y)))
        print("Test :: X shape : ", x_test.shape, "Y shape : ", y_test.shape, "Nb classes : ", len(np.unique(y)))
        print("Classes : ", np.unique(y))
        print()

        word_list.append(nb_words)
        seq_len_list.append(seq_len)
        classes.append(len(np.unique(y)))

    print("Word List : ", word_list)
    print("Sequence length list : ", seq_len_list)
    print("Max number of classes : ", classes)