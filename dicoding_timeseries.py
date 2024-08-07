# -*- coding: utf-8 -*-


Automatically generated by Colaboratory.

Original file is located at


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras.layers import Dense, LSTM
from sklearn.model_selection import train_test_split

df = pd.read_csv('/content/weatherAUS.csv')

df.head()

df.info()

df.rename(columns = {'Temp9am':'temperature'}, inplace = True)

df.isna().sum()

df['Date'] = pd.to_datetime(df['Date'])

df['Date'].head(3)

df['Temperature'].fillna(df['Temperature'].mean(), inplace=True) # we will fill the null row
df = df[['Date','Temperature' ]]
df.head()

df.info()

df['Temperature'].describe()

dates = df['Date'].values
temp = df['Temperature'].values

plt.figure(figsize=(15,5))
plt.plot(dates, temp)
plt.title('Temperature Average',
          fontsize=20)

# get data values
date = df['Date'].values
temp = df['Temperature'].values

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

x_train, x_test, y_train, y_test = train_test_split(temp, date, test_size = 0.2, random_state = 0 , shuffle=False)
print(len(x_train), len(x_test))

data_train = windowed_dataset(x_train, window_size=60, batch_size=100, shuffle_buffer=5000)
data_test = windowed_dataset(x_test, window_size=60, batch_size=100, shuffle_buffer=5000)

model = tf.keras.models.Sequential([
  tf.keras.layers.Conv1D(filters=32, kernel_size=5,
                      strides=1, padding="causal",
                      activation="relu",
                      input_shape=[None, 1]),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 400)
])

lr_schedule = tf.keras.callbacks.LearningRateScheduler(
    lambda epoch: 1e-8 * 10**(epoch / 20))
optimizer = tf.keras.optimizers.SGD(lr=1e-8, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

max = df['Temperature'].max()
print('Max value : ' )
print(max)

min = df['Temperature'].min()
print('Min Value : ')
print(min)

x = (max - min) * (10 / 100)
print(x)

x = x.round(3)

x

# callback
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')< x):
      self.model.stop_training = True
      print("\nMAE of the model < 10% of data scale")
callbacks = myCallback()

tf.keras.backend.set_floatx('float64')
history = model.fit(data_train ,epochs=500, validation_data=data_test, callbacks=[callbacks])

# plot of mae
import matplotlib.pyplot as plt
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('MAE')
plt.ylabel('mae')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# plot of loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
