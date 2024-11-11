import tensorflow as tf
from tensorflow.keras.layers import Layer

class AggregateFeatures(Layer):
    def __init__(self, **kwargs):
        super(AggregateFeatures, self).__init__(**kwargs)

    def call(self, inputs):
        words, features = inputs
        aggregated_features = tf.reduce_mean(features, axis=1)
        return tf.concat([words, aggregated_features], axis=-1)
