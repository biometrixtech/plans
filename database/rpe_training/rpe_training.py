
"""

@author: dipeshgautam
"""
import pickle
import numpy as np
import pandas as pd
# from keras.models import Sequential, Input
from keras.layers import Dense
# from sklearn.preprocessing import StandardScaler
# from scipy.signal import butter, filtfilt

from sklearn.impute import KNNImputer


def prepare_data(data):

    # %%
    total_columns = [
        'percent_hrmax',
        'percent_ftp',
        'rpe'
        ]
    data = data[total_columns]

    # %%
    # Create the training and test sets
    predictors = [
        'percent_hrmax',
        'percent_ftp'
    ]

    # imputer = KNNImputer(n_neighbors=3)
    # data_filled = imputer.fit_transform(data)
    # data.percent_hrmax.fillna(.5, inplace=True)
    # data.percent_ftp.fillna(.5, inplace=True)
    # data.percent_hrmax.fillna(np.nanmean(data.percent_hrmax), inplace=True)
    # data.percent_ftp.fillna(np.nanmean(data.percent_ftp), inplace=True)
    # data.fillna(0, inplace=True)
    # X = data_filled[:, 0:2]

    X = data[predictors].values
    Y = data['rpe'].values
    return X, Y



def train_model(data):
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers


    X, Y = prepare_data(data)
    seed = 7
    np.random.seed(seed)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=[None], ragged=True),
        tf.keras.layers.Embedding(2, 16),
        tf.keras.layers.LSTM(32, use_bias=False),
        tf.keras.layers.Dense(32, activation='relu'),
        # tf.keras.layers.Activation(tf.nn.relu),
        tf.keras.layers.Dense(1)
    ])


    inputs = keras.Input(shape=(None,),
                         batch_size=64,
                         # tensor=
                         ragged=True)
    dense1 = layers.LSTM(64,
                         kernel_initializer='normal',
                         activation="relu")
    dense2 = layers.Dense(5,
                         kernel_initializer='normal',
                         activation="relu")
    x = dense1(inputs)
    x = dense2(x)
    outputs = layers.Dense(1)(x)
    model = keras.Model(inputs=inputs, outputs=outputs, name="mnist_model")
    model.compile(
            loss='mean_squared_error',
            optimizer='Nadam'
    )
    model.fit(X, Y, batch_size=64, epochs=2, validation_split=0.2)


    # model = Sequential()
    # init = 'normal'
    # dim = X.shape[1]
    # model.add(Dense(50, input_dim=dim, kernel_initializer=init, activation='elu'))
    # # model.add(Dense(50, kernel_initializer=init, activation='elu'))
    # # model.add(Dense(100, kernel_initializer=init, activation='elu'))
    # # model.add(Dense(20, kernel_initializer=init, activation='elu'))
    # # model.add(Dense(10, kernel_initializer=init, activation='elu'))
    # model.add(Dense(5, kernel_initializer=init, activation='elu'))
    # model.add(Dense(1, kernel_initializer=init))
    # # Compile model
    # model.compile(loss='mean_squared_error', optimizer='Nadam')
    #
    # model.fit(X, Y, epochs=20, batch_size=500, verbose=1)
    return model
    # model.save('/Users/dipeshgautam/Desktop/biometrix/grf_test_v3/models/grf_model_v3_209.h5')

def train_xgb():
    import xgboost as xgb
    dtrain = xgb.DMatrix('simulated_data.csv')
    print('here')


def test_ragged():
    import tensorflow as tf
    # Task: predict whether each sentence is a question or not.
    sentences = tf.constant(
            ['What makes you think she is a witch?',
             'She turned me into a newt.',
             'A newt?',
             'Well, I got better.'])
    is_question = tf.constant([True, False, True, False])

    # Preprocess the input strings.
    hash_buckets = 1000
    words = tf.strings.split(sentences, ' ')
    hashed_words = tf.strings.to_hash_bucket_fast(words, hash_buckets)

    # Build the Keras model.
    keras_model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=[None], dtype=tf.int64, ragged=True),
        tf.keras.layers.Embedding(hash_buckets, 16),
        tf.keras.layers.LSTM(32, use_bias=False),
        tf.keras.layers.Dense(32, activation='relu'),
        # tf.keras.layers.Activation(tf.nn.relu),
        tf.keras.layers.Dense(1)
    ])

    keras_model.compile(loss='binary_crossentropy', optimizer='rmsprop')
    keras_model.fit(hashed_words, is_question, epochs=10)
    print(keras_model.predict(hashed_words))


if __name__ == '__main__':
    # test_ragged()
    # model = train_xgb()
    data = pd.read_csv('simulated_data.csv')
    model = train_model(data)
    # # test_data = np.array([1, .75]).reshape(1, -1)
    #
    # heart_rate = np.linspace(.5, 1, 50)
    # ftp = np.array([.75] * 50)
    # test_data = np.transpose(np.array([heart_rate, ftp]))
    #
    # prediction = model.predict(test_data)
    # print('here')
