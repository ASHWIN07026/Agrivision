from pathlib import Path
import tensorflow as tf
p=Path(__file__).resolve().parent
m=tf.keras.models.load_model(p/'models/disease/disease_mobilenetv2.keras',compile=False,safe_mode=True)
c=tf.lite.TFLiteConverter.from_keras_model(m)
(p/'models/disease/disease_mobilenetv2.tflite').write_bytes(c.convert())
print('Converted float32 model without quantization or retraining')
