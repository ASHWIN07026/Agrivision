import sys,io,json
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p/'backend'))
from app.ml.image_preprocessing import resize_rgb
m=tf.keras.models.load_model(p/'models/disease/disease_mobilenetv2.keras',compile=False,safe_mode=True)
it=tf.lite.Interpreter(model_path=str(p/'models/disease/disease_mobilenetv2.tflite'),num_threads=1);it.allocate_tensors()
input_index=it.get_input_details()[0]['index'];output_index=it.get_output_details()[0]['index']
results=[]
for f in sorted((p/'samples').glob('*.jpg')):
 b=f.read_bytes();im=tf.io.decode_image(b,channels=3,expand_animations=False)
 x=tf.image.resize(im,(160,160),antialias=True).numpy()[None]
 y=m.predict(x,verbose=0)[0]
 it.set_tensor(input_index,x);it.invoke();z=it.get_tensor(output_index)[0]
 # Isolate numerical resize from JPEG decoder differences.
 npresize=resize_rgb(im.numpy(),160,160)
 pil=resize_rgb(np.asarray(Image.open(io.BytesIO(b)).convert('RGB')),160,160)[None]
 it.set_tensor(input_index,pil);it.invoke();zp=it.get_tensor(output_index)[0]
 row={'image':f.name,'keras_class_index':int(y.argmax()),'litert_class_index':int(z.argmax()),'deployment_class_index':int(zp.argmax()),'same_input_max_score_error':float(abs(y-z).max()),'same_decoded_pixels_resize_max_error':float(abs(npresize-x[0]).max()),'full_pipeline_max_score_error':float(abs(y-zp).max())}
 print(row);assert row['keras_class_index']==row['deployment_class_index'];assert row['same_input_max_score_error']<0.0001;assert row['same_decoded_pixels_resize_max_error']<0.001
 results.append(row)
(p/'conversion_validation.json').write_text(json.dumps({'scope':'Three supplied sample images only; original 731-image accuracy NOT re-evaluated for LiteRT','results':results},indent=2))
