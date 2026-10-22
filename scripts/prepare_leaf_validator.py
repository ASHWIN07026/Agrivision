"""One-time preparation of fixed text embeddings for the offline CLIP gate.

Requires tokenizers and onnxruntime; runtime needs only the vision model.
Usage: python scripts/prepare_leaf_validator.py TEXT_ONNX TOKENIZER_JSON
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

POSITIVE = [
    'a photo of a single tomato plant leaf',
    'a photo of a single potato plant leaf',
    'a photo of a single bell pepper plant leaf',
    'a close-up photo of a diseased plant leaf',
    'a close-up photo of a healthy green plant leaf',
]
NEGATIVE = [
    'a photo of a person', 'a photo of a human face',
    'a photo of a hand', 'a photo of a group of people',
    'a photo of an animal', 'a photo of a cat', 'a photo of a dog',
    'a photo of a bird', 'a photo of an insect',
    'a photo of a car', 'a photo of a bus', 'a photo of a motorcycle',
    'a photo of a tractor', 'a photo of a vehicle',
    'a photo of a building', 'a photo of a road',
    'a photo of food', 'a photo of fruit', 'a photo of vegetables',
    'a photo of a flower', 'a photo of grass', 'a photo of a tree',
    'a photo of a landscape', 'a photo of a computer screen',
    'a screenshot of text', 'a photo of a document',
    'a drawing or cartoon', 'a photo of a toy', 'a photo of clothing',
    'a photo of a household object', 'a photo of a green plastic object',
]
if __name__ == '__main__':
    tokenizer = Tokenizer.from_file(sys.argv[2])
    tokenizer.enable_padding(pad_id=49407, pad_token='<|endoftext|>')
    encoded = tokenizer.encode_batch(POSITIVE + NEGATIVE)
    inputs = {'input_ids': np.array([e.ids for e in encoded], dtype=np.int64)}
    options = ort.SessionOptions(); options.intra_op_num_threads = 1
    session = ort.InferenceSession(sys.argv[1], sess_options=options, providers=['CPUExecutionProvider'])
    vectors = session.run(['text_embeds'], inputs)[0]
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    Path('models/validation/text_embeddings.json').write_text(json.dumps({
        'positive_count': len(POSITIVE), 'prompts': POSITIVE + NEGATIVE,
        'text_model_sha256': hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),
        'tokenizer_sha256': hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),
        'embeddings': vectors.tolist(),
    }))
