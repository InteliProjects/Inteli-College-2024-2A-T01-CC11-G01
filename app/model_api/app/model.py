import tensorflow as tf
from tensorflow.keras.layers import Layer
from tensorflow.keras.saving import register_keras_serializable

@register_keras_serializable()
class AggregateFeatures(Layer):
    def __init__(self, **kwargs):
        super(AggregateFeatures, self).__init__(**kwargs)

    def call(self, inputs):
        words, features = inputs
        aggregated_features = tf.reduce_mean(features, axis=1)
        return tf.concat([words, aggregated_features], axis=-1)

MODEL_PATH = 'models/best_model.keras'

def load_model():
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects={'AggregateFeatures': AggregateFeatures})
    return model
